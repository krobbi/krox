#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "common.h"
#include "compiler.h"
#include "scanner.h"

#ifdef DEBUG_PRINT_CODE
#include "debug.h"
#endif

typedef struct {
	Token current;
	Token previous;
	bool hadError;
	bool panicMode;
} Parser;

typedef enum {
	PREC_NONE,
	PREC_ASSIGNMENT, /* = */
	PREC_OR,         /* or */
	PREC_AND,        /* and */
	PREC_EQUALITY,   /* == != */
	PREC_COMPARISON, /* < > <= >= */
	PREC_TERM,       /* + - */
	PREC_FACTOR,     /* * / */
	PREC_UNARY,      /* ! - */
	PREC_CALL,       /* . () */
	PREC_PRIMARY
} Precedence;

typedef void (*ParseFn)(bool canAssign);

typedef struct {
	ParseFn prefix;
	ParseFn infix;
	Precedence precedence;
} ParseRule;

typedef struct {
	Token name;
	int depth;
} Local;

typedef struct {
	Local locals[UINT8_COUNT];
	int localCount;
	int scopeDepth;
} Compiler;

Parser parser;
Compiler* current = NULL;
Chunk* compilingChunk;

/* Return a pointer to the current chunk. */
static Chunk* currentChunk() {
	return compilingChunk;
}

/* Log an error message at a token. */
static void errorAt(Token* token, const char* message) {
	/* Avoid cascading errors. */
	if (parser.panicMode) {
		return;
	}
	
	parser.panicMode = true;
	fprintf(stderr, "[line %d] Error", token->line);
	
	if (token->type == TOKEN_EOF) {
		fprintf(stderr, " at end");
	} else if (token->type == TOKEN_ERROR) {
		/* No position information. */
	} else {
		fprintf(stderr, " at '%.*s'", token->length, token->start);
	}
	
	fprintf(stderr, ": %s\n", message);
	parser.hadError = true;
}

/* Log an error message at the previous token. */
static void error(const char* message) {
	errorAt(&parser.previous, message);
}

/* Log an error message at the current token. */
static void errorAtCurrent(const char* message) {
	errorAt(&parser.current, message);
}

/* Advance to the next valid token. */
static void advance() {
	parser.previous = parser.current;
	
	for (;;) {
		parser.current = scanToken();
		
		if (parser.current.type != TOKEN_ERROR) {
			break;
		}
		
		errorAtCurrent(parser.current.start);
	}
}

/*
* Consume the current token if it matches a token type. Otherwise, log an error
* message.
*/
static void consume(TokenType type, const char* message) {
	if (parser.current.type == type) {
		advance();
		return;
	}
	
	errorAtCurrent(message);
}

/* Return whether the current token matches a token type. */
static bool check(TokenType type) {
	return parser.current.type == type;
}

/*
* Consume the current token if it matches a token type and return whether the
* current token was consumed.
*/
static bool match(TokenType type) {
	if (!check(type)) {
		return false;
	}
	
	advance();
	return true;
}

/* Emit a byte to the current chunk. */
static void emitByte(uint8_t byte) {
	writeChunk(currentChunk(), byte, parser.previous.line);
}

/* Emit 2 bytes to the current chunk. */
static void emitBytes(uint8_t byte1, uint8_t byte2) {
	emitByte(byte1);
	emitByte(byte2);
}

/* Emit a return instruction to the current chunk. */
static void emitReturn() {
	emitByte(OP_RETURN);
}

/*
* Make and return constant ID in the current chunk from a value. Log an error
* message if the current chunk is out of constants.
*/
static uint8_t makeConstant(Value value) {
	int constant = addConstant(currentChunk(), value);
	
	if ((uint32_t)constant > UINT8_MAX) {
		error("Too many constants in one chunk.");
		return 0;
	}
	
	return (uint8_t)constant;
}

/* Emit a constant instruction to the current chunk. */
static void emitConstant(Value value) {
	emitBytes(OP_CONSTANT, makeConstant(value));
}

/* Initialize the current compiler. */
static void initCompiler(Compiler* compiler) {
	compiler->localCount = 0;
	compiler->scopeDepth = 0;
	current = compiler;
}

/* End compilation. */
static void endCompiler() {
	emitReturn();
#ifdef DEBUG_PRINT_CODE
	if (!parser.hadError) {
		disassembleChunk(currentChunk(), "code");
	}
#endif
}

/* Begin a new scope. */
static void beginScope() {
	current->scopeDepth++;
}

/* End the current scope. */
static void endScope() {
	current->scopeDepth--;
	
	/* Pop locals from the stack. */
	while (
		current->localCount > 0
		&& current->locals[current->localCount - 1].depth > current->scopeDepth
	) {
		emitByte(OP_POP);
		current->localCount--;
	}
}

/* Forward declare some parsing functions. */
static uint8_t identifierConstant(Token* name);
static int resolveLocal(Compiler* compiler, Token* name);
static void expression();
static void statement();
static void declaration();
static ParseRule* getRule(TokenType type);
static void parsePrecedence(Precedence precedence);

/* Compile a binary expression. */
static void binary(bool canAssign) {
	TokenType operatorType = parser.previous.type;
	ParseRule* rule = getRule(operatorType);
	parsePrecedence((Precedence)(rule->precedence + 1));
	
	switch (operatorType) {
		case TOKEN_BANG_EQUAL:    emitBytes(OP_EQUAL, OP_NOT);   break;
		case TOKEN_EQUAL_EQUAL:   emitByte(OP_EQUAL);            break;
		case TOKEN_GREATER:       emitByte(OP_GREATER);          break;
		case TOKEN_GREATER_EQUAL: emitBytes(OP_LESS, OP_NOT);    break;
		case TOKEN_LESS:          emitByte(OP_LESS);             break;
		case TOKEN_LESS_EQUAL:    emitBytes(OP_GREATER, OP_NOT); break;
		case TOKEN_PLUS:          emitByte(OP_ADD);              break;
		case TOKEN_MINUS:         emitByte(OP_SUBTRACT);         break;
		case TOKEN_STAR:          emitByte(OP_MULTIPLY);         break;
		case TOKEN_SLASH:         emitByte(OP_DIVIDE);           break;
		default: return; /* Unreachable. */
	}
}

/* Compile a literal expression. */
static void literal(bool canAssign) {
	switch (parser.previous.type) {
		case TOKEN_FALSE: emitByte(OP_FALSE); break;
		case TOKEN_NIL:   emitByte(OP_NIL);   break;
		case TOKEN_TRUE:  emitByte(OP_TRUE);  break;
		default: return; /* Unreachable. */
	}
}

/* Compile a grouping expression. */
static void grouping(bool canAssign) {
	expression();
	consume(TOKEN_RIGHT_PAREN, "Expect ')' after expression.");
}

/* Compile a number expression. */
static void number(bool canAssign) {
	double value = strtod(parser.previous.start, NULL);
	emitConstant(NUMBER_VAL(value));
}

/* Compile a string expression. */
static void string(bool canAssign) {
	emitConstant(OBJ_VAL(copyString(parser.previous.start + 1, parser.previous.length - 2)));
}

/* Compile a variable expression from its name. */
static void namedVariable(Token name, bool canAssign) {
	uint8_t getOp, setOp;
	int arg = resolveLocal(current, &name);
	
	if (arg != -1) {
		getOp = OP_GET_LOCAL;
		setOp = OP_SET_LOCAL;
	} else {
		arg = identifierConstant(&name);
		getOp = OP_GET_GLOBAL;
		setOp = OP_SET_GLOBAL;
	}
	
	if (canAssign && match(TOKEN_EQUAL)) {
		expression();
		emitBytes(setOp, (uint8_t)arg);
	} else {
		emitBytes(getOp, (uint8_t)arg);
	}
}

/* Compile a variable expresison. */
static void variable(bool canAssign) {
	namedVariable(parser.previous, canAssign);
}

/* Compile a unary expression. */
static void unary(bool canAssign) {
	TokenType operatorType = parser.previous.type;
	
	/* Compile the operand. */
	parsePrecedence(PREC_UNARY);
	
	/* Compile the operator. */
	switch (operatorType) {
		case TOKEN_MINUS: emitByte(OP_NEGATE); break;
		case TOKEN_BANG:  emitByte(OP_NOT);    break;
		default: return; /* Unreachable. */
	}
}

ParseRule rules[] = {
	[TOKEN_LEFT_PAREN]    = {grouping, NULL,   PREC_NONE},
	[TOKEN_RIGHT_PAREN]   = {NULL,     NULL,   PREC_NONE},
	[TOKEN_LEFT_BRACE]    = {NULL,     NULL,   PREC_NONE},
	[TOKEN_RIGHT_BRACE]   = {NULL,     NULL,   PREC_NONE},
	[TOKEN_COMMA]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_DOT]           = {NULL,     NULL,   PREC_NONE},
	[TOKEN_MINUS]         = {unary,    binary, PREC_TERM},
	[TOKEN_PLUS]          = {NULL,     binary, PREC_TERM},
	[TOKEN_SEMICOLON]     = {NULL,     NULL,   PREC_NONE},
	[TOKEN_SLASH]         = {NULL,     binary, PREC_FACTOR},
	[TOKEN_STAR]          = {NULL,     binary, PREC_FACTOR},
	[TOKEN_BANG]          = {unary,    NULL,   PREC_NONE},
	[TOKEN_BANG_EQUAL]    = {NULL,     binary, PREC_EQUALITY},
	[TOKEN_EQUAL]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_EQUAL_EQUAL]   = {NULL,     binary, PREC_EQUALITY},
	[TOKEN_GREATER]       = {NULL,     binary, PREC_COMPARISON},
	[TOKEN_GREATER_EQUAL] = {NULL,     binary, PREC_COMPARISON},
	[TOKEN_LESS]          = {NULL,     binary, PREC_COMPARISON},
	[TOKEN_LESS_EQUAL]    = {NULL,     binary, PREC_COMPARISON},
	[TOKEN_IDENTIFIER]    = {variable, NULL,   PREC_NONE},
	[TOKEN_STRING]        = {string,   NULL,   PREC_NONE},
	[TOKEN_NUMBER]        = {number,   NULL,   PREC_NONE},
	[TOKEN_AND]           = {NULL,     NULL,   PREC_NONE},
	[TOKEN_CLASS]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_ELSE]          = {NULL,     NULL,   PREC_NONE},
	[TOKEN_FALSE]         = {literal,  NULL,   PREC_NONE},
	[TOKEN_FOR]           = {NULL,     NULL,   PREC_NONE},
	[TOKEN_FUN]           = {NULL ,    NULL,   PREC_NONE},
	[TOKEN_IF]            = {NULL,     NULL,   PREC_NONE},
	[TOKEN_NIL]           = {literal,  NULL,   PREC_NONE},
	[TOKEN_OR]            = {NULL,     NULL,   PREC_NONE},
	[TOKEN_PRINT]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_RETURN]        = {NULL,     NULL,   PREC_NONE},
	[TOKEN_SUPER]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_THIS]          = {NULL,     NULL,   PREC_NONE},
	[TOKEN_TRUE]          = {literal,  NULL,   PREC_NONE},
	[TOKEN_VAR]           = {NULL,     NULL,   PREC_NONE},
	[TOKEN_WHILE]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_ERROR]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_EOF]           = {NULL,     NULL,   PREC_NONE},
};

/* Parse an expression with a precedence level. */
static void parsePrecedence(Precedence precedence) {
	advance();
	ParseFn prefixRule = getRule(parser.previous.type)->prefix;
	
	if (prefixRule == NULL) {
		error("Expect expression.");
		return;
	}
	
	bool canAssign = precedence <= PREC_ASSIGNMENT;
	prefixRule(canAssign);
	
	while (precedence <= getRule(parser.current.type)->precedence) {
		advance();
		ParseFn infixRule = getRule(parser.previous.type)->infix;
		infixRule(canAssign);
	}
	
	if (canAssign && match(TOKEN_EQUAL)) {
		error("Invalid assignment target.");
	}
}

/* Return an identifier's constant ID from its name. */
static uint8_t identifierConstant(Token* name) {
	return makeConstant(OBJ_VAL(copyString(name->start, name->length)));
}

/* Return whether two identifier tokens are equal. */
static bool identifiersEqual(Token* a, Token* b) {
	if(a->length != b->length) {
		return false;
	}
	
	return memcmp(a->start, b->start, a->length) == 0;
}

/*
* Resolve and return a variable's local offset. Return -1 if the variable is not
* local.
*/
static int resolveLocal(Compiler* compiler, Token* name) {
	for (int i = compiler->localCount - 1; i >= 0; i--) {
		Local* local = &compiler->locals[i];
		
		if (identifiersEqual(name, &local->name)) {
			if (local->depth == -1) {
				error("Can't read local variable in its own initializer.");
			}
			
			return i;
		}
	}
	
	return -1;
}

/* Add a local variable from its name. */
static void addLocal(Token name) {
	if (current->localCount == UINT8_COUNT) {
		error("Too many local variables in function.");
		return;
	}
	
	/* The local's depth is set to -1 until it is initialized. */
	Local* local = &current->locals[current->localCount++];
	local->name = name;
	local->depth = -1;
}

/* Declare a local variable. */
static void declareVariable() {
	/* Don't declare a local if we are in the global scope. */
	if (current->scopeDepth == 0) {
		return;
	}
	
	Token* name = &parser.previous;
	
	for (int i = current->localCount - 1; i >= 0; i--) {
		Local* local = &current->locals[i];
		
		if(local->depth != -1 && local->depth < current->scopeDepth) {
			break;
		}
		
		if (identifiersEqual(name, &local->name)) {
			error("Already a variable with this name in this scope.");
		}
	}
	
	addLocal(*name);
}

/* Parse a variable's constant ID. */
static uint8_t parseVariable(const char* errorMessage) {
	consume(TOKEN_IDENTIFIER, errorMessage);
	declareVariable();
	
	/* Don't create a constant ID if we are a local variable. */
	if (current->scopeDepth > 0) {
		return 0;
	}
	
	return identifierConstant(&parser.previous);
}

/* Mark the current local variable as initialized. */
static void markInitialized() {
	current->locals[current->localCount - 1].depth = current->scopeDepth;
}

/* Define a variable from its constant ID. */
static void defineVariable(uint8_t global) {
	/* Don't define a global if we are a local variable. */
	if (current->scopeDepth > 0) {
		markInitialized();
		return;
	}
	
	emitBytes(OP_DEFINE_GLOBAL, global);
}

/* Return a pointer to a parse rule from a token type. */
static ParseRule* getRule(TokenType type) {
	return &rules[type];
}

/* Compile an expression. */
static void expression() {
	parsePrecedence(PREC_ASSIGNMENT);
}

/* Compile a block. */
static void block() {
	while (!check(TOKEN_RIGHT_BRACE) && !check(TOKEN_EOF)) {
		declaration();
	}
	
	consume(TOKEN_RIGHT_BRACE, "Expect '}' after block.");
}

/* Compile a variable declaration. */
static void varDeclaration() {
	uint8_t global = parseVariable("Expect variable name.");
	
	if (match(TOKEN_EQUAL)) {
		expression();
	} else {
		emitByte(OP_NIL);
	}
	
	consume(TOKEN_SEMICOLON, "Expect ';' after variable expression.");
	defineVariable(global);
}

/* Compile an expression statement. */
static void expressionStatement() {
	expression();
	consume(TOKEN_SEMICOLON, "Expect ';' after expression.");
	emitByte(OP_POP);
}

/* Compile a print statement. */
static void printStatement() {
	expression();
	consume(TOKEN_SEMICOLON, "Expect ';' after value.");
	emitByte(OP_PRINT);
}

/* Synchronize the parser out of panic mode. */
static void synchronize() {
	parser.panicMode = false;
	
	while (parser.current.type != TOKEN_EOF) {
		/* At the end of a statement. */
		if (parser.previous.type == TOKEN_SEMICOLON) {
			return;
		}
		
		switch (parser.current.type) {
			case TOKEN_CLASS:
			case TOKEN_FUN:
			case TOKEN_VAR:
			case TOKEN_FOR:
			case TOKEN_IF:
			case TOKEN_WHILE:
			case TOKEN_PRINT:
			case TOKEN_RETURN:
				return; /* Found a possible statement. */
			default: break; /* Do nothing. */
		}
		
		advance();
	}
}

/* Compile a declaration. */
static void declaration() {
	if (match(TOKEN_VAR)) {
		varDeclaration();
	} else {
		statement();
	}
	
	if (parser.panicMode) {
		synchronize();
	}
}

/* Compile a statement. */
static void statement() {
	if (match(TOKEN_PRINT)) {
		printStatement();
	} else if (match(TOKEN_LEFT_BRACE)) {
		beginScope();
		block();
		endScope();
	} else {
		expressionStatement();
	}
}

/* Compile Krox source code. */
bool compile(const char* source, Chunk* chunk) {
	initScanner(source);
	Compiler compiler;
	initCompiler(&compiler);
	compilingChunk = chunk;
	
	parser.hadError = false;
	parser.panicMode = false;
	
	advance();
	
	while (!match(TOKEN_EOF)) {
		declaration();
	}
	
	endCompiler();
	return !parser.hadError;
}