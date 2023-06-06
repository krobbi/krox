#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "common.h"
#include "compiler.h"
#include "memory.h"
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
	bool isCaptured;
} Local;

typedef struct {
	uint8_t index;
	bool isLocal;
} Upvalue;

typedef enum {
	TYPE_FUNCTION,
	TYPE_INITIALIZER,
	TYPE_METHOD,
	TYPE_SCRIPT,
} FunctionType;

typedef struct {
	struct Compiler* enclosing;
	ObjFunction* function;
	FunctionType type;
	Local locals[UINT8_COUNT];
	int localCount;
	Upvalue upvalues[UINT8_COUNT];
	int scopeDepth;
} Compiler;

typedef struct ClassCompiler {
	struct ClassCompiler* enclosing;
	bool hasSuperclass;
} ClassCompiler;

typedef uint16_t ConstantID;

Parser parser;
Compiler* current = NULL;
ClassCompiler* currentClass = NULL;

/* Return a pointer to the current chunk. */
static Chunk* currentChunk() {
	return &current->function->chunk;
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

/* Emit a constant ID to the current chunk. */
static void emitConstantID(ConstantID id) {
	emitByte((id >> 8) & 0xff);
	emitByte(id & 0xff);
}

/* Emit a loop instruction to an previous offset. */
static void emitLoop(int loopStart) {
	emitByte(OP_LOOP);
	
	/* Jump distance. Add 2 to account for the distance operand. */
	int offset = currentChunk()->count - loopStart + 2;
	
	if ((uint32_t)offset > UINT16_MAX) {
		error("Loop body too large.");
	}
	
	emitByte((offset >> 8) & 0xff);
	emitByte(offset & 0xff);
}

/*
* Emit a jump instruction to the current chunk and return the offset to patch
* the distance operand to.
*/
static int emitJump(uint8_t instruction) {
	emitByte(instruction);
	emitByte(0xff);
	emitByte(0xff);
	return currentChunk()->count - 2;
}

/* Emit an implicit return instruction to the current chunk. */
static void emitReturn() {
	if (current->type == TYPE_INITIALIZER) {
		emitBytes(OP_GET_LOCAL, 0);
	} else {
		emitByte(OP_NIL);
	}
	
	emitByte(OP_RETURN);
}

/*
* Make and return a constant ID in the current chunk from a value. Log an error
* message if the current chunk is out of constants.
*/
static ConstantID makeConstant(Value value) {
	int constant = addConstant(currentChunk(), value);
	
	if ((uint32_t)constant > UINT16_MAX) {
		error("Too many constants in one chunk.");
		return 0;
	}
	
	return (ConstantID)constant;
}

/* Emit a constant instruction to the current chunk. */
static void emitConstant(Value value) {
	emitByte(OP_CONSTANT);
	emitConstantID(makeConstant(value));
}

/* Backpatch a jump instruction's distance operand at an offset. */
static void patchJump(int offset) {
	/* Jump distance. Subtract 2 to account for the distance operand. */
	int jump = currentChunk()->count - offset - 2;
	
	if ((uint32_t)jump > UINT16_MAX) {
		error("Too much code to jump over.");
	}
	
	currentChunk()->code[offset] = (jump >> 8) & 0xff;
	currentChunk()->code[offset + 1] = jump & 0xff;
}

/* Initialize the current compiler. */
static void initCompiler(Compiler* compiler, FunctionType type) {
	compiler->enclosing = (struct Compiler*)current;
	compiler->function = NULL;
	compiler->type = type;
	compiler->localCount = 0;
	compiler->scopeDepth = 0;
	compiler->function = newFunction();
	current = compiler;
	
	if (type != TYPE_SCRIPT) {
		current->function->name = copyString(parser.previous.start, parser.previous.length);
	}
	
	/* Reserve local slot 0 for internal use. */
	Local* local = &current->locals[current->localCount++];
	local->depth = 0;
	local->isCaptured = false;
	
	if (type != TYPE_FUNCTION) {
		local->name.start = "this";
		local->name.length = 4;
	} else {
		local->name.start = "";
		local->name.length = 0;
	}
}

/* End compilation. */
static ObjFunction* endCompiler() {
	emitReturn();
	ObjFunction* function = current->function;
	
#ifdef DEBUG_PRINT_CODE
	if (!parser.hadError) {
		disassembleChunk(
			currentChunk(), function->name != NULL ? function->name->chars : "<script>"
		);
	}
#endif
	
	current = (Compiler*)current->enclosing;
	return function;
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
		/* Move the value to the heap if it's used in a closure. */
		if (current->locals[current->localCount - 1].isCaptured) {
			emitByte(OP_CLOSE_UPVALUE);
		} else {
			emitByte(OP_POP);
		}
		
		current->localCount--;
	}
}

/* Forward declare some parsing functions. */
static uint8_t argumentList();
static ConstantID identifierConstant(Token* name);
static int resolveLocal(Compiler* compiler, Token* name);
static int resolveUpvalue(Compiler* compiler, Token* name);
static void and_(bool canAssign);
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

/* Compile a call expression. */
static void call(bool canAssign) {
	uint8_t argCount = argumentList();
	emitBytes(OP_CALL, argCount);
}

/* Compile a dot expression. */
static void dot(bool canAssign) {
	consume(TOKEN_IDENTIFIER, "Expect property name after '.'.");
	ConstantID name = identifierConstant(&parser.previous);
	
	if (canAssign && match(TOKEN_EQUAL)) {
		expression();
		emitByte(OP_SET_PROPERTY);
		emitConstantID(name);
	} else if (match(TOKEN_LEFT_PAREN)) {
		uint8_t argCount = argumentList();
		emitByte(OP_INVOKE);
		emitConstantID(name);
		emitByte(argCount);
	} else {
		emitByte(OP_GET_PROPERTY);
		emitConstantID(name);
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

/* Compile an or expression. */
static void or_(bool canAssign) {
	/* Try the second operand if the first operand was falsey. */
	int elseJump = emitJump(OP_JUMP_IF_FALSE);
	int endJump = emitJump(OP_JUMP); /* Short circuit if truthy. */
	
	patchJump(elseJump); /* Begin second operand. */
	emitByte(OP_POP); /* Discard first operand. */
	parsePrecedence(PREC_OR); /* Use second operand instead. */
	
	patchJump(endJump); /* Mark the end of the short circuit. */
}

/* Compile a string expression. */
static void string(bool canAssign) {
	emitConstant(OBJ_VAL(copyString(parser.previous.start + 1, parser.previous.length - 2)));
}

/* Compile a variable expression from its name. */
static void namedVariable(Token name, bool canAssign) {
	uint8_t getOp, setOp;
	int arg = resolveLocal(current, &name);
	bool isArgConstantID = false;
	
	if (arg != -1) {
		getOp = OP_GET_LOCAL;
		setOp = OP_SET_LOCAL;
	} else if ((arg = resolveUpvalue(current, &name)) != -1) {
		getOp = OP_GET_UPVALUE;
		setOp = OP_SET_UPVALUE;
	} else {
		arg = identifierConstant(&name);
		isArgConstantID = true;
		getOp = OP_GET_GLOBAL;
		setOp = OP_SET_GLOBAL;
	}
	
	if (canAssign && match(TOKEN_EQUAL)) {
		expression();
		emitByte(setOp);
	} else {
		emitByte(getOp);
	}
	
	if(isArgConstantID){
		emitConstantID((ConstantID)arg);
	} else {
		emitByte((uint8_t)arg);
	}
}

/* Compile a variable expresison. */
static void variable(bool canAssign) {
	namedVariable(parser.previous, canAssign);
}

/* Create and return a new synthetic token from its lexeme. */
static Token syntheticToken(const char* text) {
	Token token;
	token.start = text;
	token.length = (int)strlen(text);
	return token;
}

/* Compile a super expression. */
static void super_(bool canAssign) {
	if (currentClass == NULL) {
		error("Can't use 'super' outside of a class.");
	} else if (!currentClass->hasSuperclass) {
		error("Can't use 'super' in a class with no superclass.");
	}
	
	consume(TOKEN_DOT, "Expect '.' after 'super'.");
	consume(TOKEN_IDENTIFIER, "Expect superclass method name.");
	ConstantID name = identifierConstant(&parser.previous);
	
	namedVariable(syntheticToken("this"), false);
	
	if (match(TOKEN_LEFT_PAREN)) {
		uint8_t argCount = argumentList();
		namedVariable(syntheticToken("super"), false);
		emitByte(OP_SUPER_INVOKE);
		emitConstantID(name);
		emitByte(argCount);
	} else {
		namedVariable(syntheticToken("super"), false);
		emitByte(OP_GET_SUPER);
		emitConstantID(name);
	}
}

/* Compile a this expression. */
static void this_(bool canAssign) {
	if (currentClass == NULL) {
		error("Can't use 'this' outside of a class.");
		return;
	}
	
	variable(false);
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
	[TOKEN_LEFT_PAREN]    = {grouping, call,   PREC_CALL},
	[TOKEN_RIGHT_PAREN]   = {NULL,     NULL,   PREC_NONE},
	[TOKEN_LEFT_BRACE]    = {NULL,     NULL,   PREC_NONE},
	[TOKEN_RIGHT_BRACE]   = {NULL,     NULL,   PREC_NONE},
	[TOKEN_COMMA]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_DOT]           = {NULL,     dot,    PREC_CALL},
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
	[TOKEN_AND]           = {NULL,     and_,   PREC_AND},
	[TOKEN_CLASS]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_ELSE]          = {NULL,     NULL,   PREC_NONE},
	[TOKEN_FALSE]         = {literal,  NULL,   PREC_NONE},
	[TOKEN_FOR]           = {NULL,     NULL,   PREC_NONE},
	[TOKEN_FUN]           = {NULL ,    NULL,   PREC_NONE},
	[TOKEN_IF]            = {NULL,     NULL,   PREC_NONE},
	[TOKEN_NIL]           = {literal,  NULL,   PREC_NONE},
	[TOKEN_OR]            = {NULL,     or_,    PREC_OR},
	[TOKEN_PRINT]         = {NULL,     NULL,   PREC_NONE},
	[TOKEN_RETURN]        = {NULL,     NULL,   PREC_NONE},
	[TOKEN_SUPER]         = {super_,   NULL,   PREC_NONE},
	[TOKEN_THIS]          = {this_,    NULL,   PREC_NONE},
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
static ConstantID identifierConstant(Token* name) {
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

/*
* Add a new upvalue to the current function's compiler and return its offset.
*/
static int addUpvalue(Compiler* compiler, uint8_t index, bool isLocal) {
	int upvalueCount = compiler->function->upvalueCount;
	
	for (int i = 0; i < upvalueCount; i++) {
		Upvalue* upvalue = &compiler->upvalues[i];
		
		if (upvalue->index == index && upvalue->isLocal == isLocal) {
			return i;
		}
	}
	
	if (upvalueCount == UINT8_COUNT) {
		error("Too many closure variables in function.");
		return 0;
	}
	
	compiler->upvalues[upvalueCount].isLocal = isLocal;
	compiler->upvalues[upvalueCount].index = index;
	return compiler->function->upvalueCount++;
}

/*
* Resolve and return a variables upvalue offset. Return -1 if the variable is
* not an upvalue.
*/
static int resolveUpvalue(Compiler* compiler, Token* name) {
	if (compiler->enclosing == NULL) {
		return -1;
	}
	
	int local = resolveLocal((Compiler*)(compiler->enclosing), name);
	
	if (local != -1) {
		/* Workaround for weird bug, maybe an issue with the typedef? */
		Compiler* enclosing = (Compiler*)(compiler->enclosing);
		
		enclosing->locals[local].isCaptured = true;
		return addUpvalue(compiler, (uint8_t)local, true);
	}
	
	int upvalue = resolveUpvalue((Compiler*)(compiler->enclosing), name);
	
	if (upvalue != -1) {
		return addUpvalue(compiler, (uint8_t)upvalue, false);
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
	local->isCaptured = false;
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
static ConstantID parseVariable(const char* errorMessage) {
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
	if (current->scopeDepth == 0) {
		return; /* Do nothing if we are in the global scope. */
	}
	
	current->locals[current->localCount - 1].depth = current->scopeDepth;
}

/* Define a variable from its constant ID. */
static void defineVariable(ConstantID global) {
	/* Don't define a global if we are a local variable. */
	if (current->scopeDepth > 0) {
		markInitialized();
		return;
	}
	
	emitByte(OP_DEFINE_GLOBAL);
	emitConstantID(global);
}

/* Compile an argument list and return an argument count. */
static uint8_t argumentList() {
	uint8_t argCount = 0;
	
	if (!check(TOKEN_RIGHT_PAREN)) {
		do {
			expression();
			
			if (argCount == 255) {
				error("Can't have more than 255 arguments.");
			}
			
			argCount++;
		} while (match(TOKEN_COMMA));
	}
	
	consume(TOKEN_RIGHT_PAREN, "Expect ')' after arguments.");
	return argCount;
}

/* Compile an and expression. */
static void and_(bool canAssign) {
	/* Short circuit if the first operand was falsey.*/
	int endJump = emitJump(OP_JUMP_IF_FALSE);
	
	emitByte(OP_POP); /* Otherwise, discard the first operand. */
	parsePrecedence(PREC_AND); /* Use the second operand instead. */
	
	patchJump(endJump); /* Mark the end of the short circuit. */
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

/* Compile a function from its type. */
static void function(FunctionType type) {
	Compiler compiler; /* Each function is compiled as its own unit. */
	initCompiler(&compiler, type);
	beginScope(); /* Function parameters are always locals. */
	
	consume(TOKEN_LEFT_PAREN, "Expect '(' after function name.");
	
	if (!check(TOKEN_RIGHT_PAREN)) {
		do {
			current->function->arity++;
			
			if (current->function->arity > 255) {
				errorAtCurrent("Can't have more than 255 parameters.");
			}
			
			ConstantID constant = parseVariable("Expect parameter name.");
			defineVariable(constant);
		} while (match(TOKEN_COMMA));
	}
	
	consume(TOKEN_RIGHT_PAREN, "Expect ')' after parameters.");
	consume(TOKEN_LEFT_BRACE, "Expect '{' before function body.");
	block();
	
	ObjFunction* function = endCompiler();
	emitByte(OP_CLOSURE);
	emitConstantID(makeConstant(OBJ_VAL(function)));
	
	for (int i = 0; i < function->upvalueCount; i++) {
		emitByte(compiler.upvalues[i].isLocal ? 1 : 0);
		emitByte(compiler.upvalues[i].index);
	}
}

/* Compile a method declaration. */
static void method() {
	consume(TOKEN_IDENTIFIER, "Expect method name.");
	ConstantID constant = identifierConstant(&parser.previous);
	FunctionType type = TYPE_METHOD;
	
	if (parser.previous.length == 4 && memcmp(parser.previous.start, "init", 4) == 0) {
		type = TYPE_INITIALIZER;
	}
	
	function(type);
	emitByte(OP_METHOD);
	emitConstantID(constant);
}

/* Compile a class declaration. */
static void classDeclaration() {
	consume(TOKEN_IDENTIFIER, "Expect class name.");
	Token className = parser.previous;
	ConstantID nameConstant = identifierConstant(&parser.previous);
	declareVariable();
	
	emitByte(OP_CLASS);
	emitConstantID(nameConstant);
	defineVariable(nameConstant);
	
	ClassCompiler classCompiler;
	classCompiler.hasSuperclass = false;
	classCompiler.enclosing = currentClass;
	currentClass = &classCompiler;
	
	if (match(TOKEN_LESS)) {
		consume(TOKEN_IDENTIFIER, "Expect superclass name.");
		variable(false);
		
		if (identifiersEqual(&className, &parser.previous)) {
			error("A class can't inherit from itself.");
		}
		
		beginScope();
		addLocal(syntheticToken("super"));
		defineVariable(0);
		
		namedVariable(className, false);
		emitByte(OP_INHERIT);
		classCompiler.hasSuperclass = true;
	}
	
	namedVariable(className, false); /* Push class for method declarations. */
	consume(TOKEN_LEFT_BRACE, "Expect '{' before class body.");
	
	while (!check(TOKEN_RIGHT_BRACE) && !check(TOKEN_EOF)) {
		method();
	}
	
	consume(TOKEN_RIGHT_BRACE, "Expect '}' after class body.");
	emitByte(OP_POP); /* Discard class from stack. */
	
	if (classCompiler.hasSuperclass) {
		endScope(); /* Discard super variable. */
	}
	
	currentClass = currentClass->enclosing;
}

/* Compile a function declaration. */
static void funDeclaration() {
	ConstantID global = parseVariable("Expect function name.");
	markInitialized();
	function(TYPE_FUNCTION);
	defineVariable(global);
}

/* Compile a variable declaration. */
static void varDeclaration() {
	ConstantID global = parseVariable("Expect variable name.");
	
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

/* Compile a for statement. */
static void forStatement() {
	beginScope(); /* Ensure any initializer variables are locals. */
	consume(TOKEN_LEFT_PAREN, "Expect '(' after 'for'.");
	
	if (match(TOKEN_SEMICOLON)) {
		/* No initializer. Do nothing. */
	} else if (match(TOKEN_VAR)) {
		varDeclaration();
	} else {
		expressionStatement();
	}
	
	int loopStart = currentChunk()->count; /* Mark start of loop condition. */
	int exitJump = -1; /* Exit offset. -1 for an infinite loop. */
	
	/* We are in an infinite loop if there is no condition. */
	if (!match(TOKEN_SEMICOLON)) {
		expression(); /* Loop condition. */
		consume(TOKEN_SEMICOLON, "Expect ';' after loop condition.");
		
		/* Exit loop if condition is falsey. */
		exitJump = emitJump(OP_JUMP_IF_FALSE);
		emitByte(OP_POP); /* Discard loop condition. */
	}
	
	/* Wire up increment clauses with convoluted single-pass spaghetti. */
	if(!match(TOKEN_RIGHT_PAREN)) {
		/* Jump over increment clause to run body first. */
		int bodyJump = emitJump(OP_JUMP);
		
		/* Mark start of increment clause. */
		int incrementStart = currentChunk()->count;
		expression(); /* Increment clause. */
		emitByte(OP_POP); /* Discard result of increment clause. */
		consume(TOKEN_RIGHT_PAREN, "Expect ';' after for clauses.");
		
		emitLoop(loopStart); /* Jump back to the loop condition. */
		/* Redirect the end of the loop body to the increment clause. */
		loopStart = incrementStart;
		patchJump(bodyJump); /* Finish jumping over increment clause. */
	}
	
	statement();
	emitLoop(loopStart);
	
	/* Patch exit jump if we are not in an infinite loop. */
	if (exitJump != -1) {
		patchJump(exitJump);
		emitByte(OP_POP); /* Discard loop condition. */
	}
	
	endScope();
}

/* Compile an if statement. */
static void ifStatement() {
	consume(TOKEN_LEFT_PAREN, "Expect '(' after 'if'.");
	expression();
	consume(TOKEN_RIGHT_PAREN, "Expect ')' after condition.");
	
	/* Jump over the then clause if the condition is false. */
	int thenJump = emitJump(OP_JUMP_IF_FALSE);
	emitByte(OP_POP); /* Pop the condition from the stack. */
	statement(); /* Then clause body. */
	int elseJump = emitJump(OP_JUMP); /* Jump over the else clause. */
	
	/* Begin the else clause. */
	patchJump(thenJump);
	emitByte(OP_POP); /* Pop the condition, even if we have no else clause. */
	
	if (match(TOKEN_ELSE)) {
		statement(); /* Else clause body. */
	}
	
	patchJump(elseJump); /* Mark the end of the else clause. */
}

/* Compile a print statement. */
static void printStatement() {
	expression();
	consume(TOKEN_SEMICOLON, "Expect ';' after value.");
	emitByte(OP_PRINT);
}

/* Compile a return statement. */
static void returnStatement() {
	if (current->type == TYPE_SCRIPT) {
		error("Can't return from top-level code.");
	}
	
	if (match(TOKEN_SEMICOLON)) {
		emitReturn();
	} else {
		if (current->type == TYPE_INITIALIZER) {
			error("Can't return a value from an initializer.");
		}
		
		expression();
		consume(TOKEN_SEMICOLON, "Expect ';' after return value.");
		emitByte(OP_RETURN);
	}
}

/* Compile a while statement. */
static void whileStatement() {
	/* Mark the start of the loop condition. */
	int loopStart = currentChunk()->count;
	consume(TOKEN_LEFT_PAREN, "Expect '(' after 'while'.");
	expression();
	consume(TOKEN_RIGHT_PAREN, "Expect ')' after condition.");
	
	int exitJump = emitJump(OP_JUMP_IF_FALSE);
	emitByte(OP_POP); /* Pop loop condition. */
	statement(); /* Loop body. */
	emitLoop(loopStart); /* Jump back to loop condition. */
	
	patchJump(exitJump); /* Mark end of loop. */
	emitByte(OP_POP); /* Pop loop condition. */
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
	if (match(TOKEN_CLASS)) {
		classDeclaration();
	} else if (match(TOKEN_FUN)) {
		funDeclaration();
	} else if (match(TOKEN_VAR)) {
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
	} else if (match(TOKEN_FOR)) {
		forStatement();
	} else if (match(TOKEN_IF)) {
		ifStatement();
	} else if (match(TOKEN_RETURN)) {
		returnStatement();
	} else if (match(TOKEN_WHILE)) {
		whileStatement();
	} else if (match(TOKEN_LEFT_BRACE)) {
		beginScope();
		block();
		endScope();
	} else {
		expressionStatement();
	}
}

/* Compile Lox source code. */
ObjFunction* compile(const char* source) {
	initScanner(source);
	Compiler compiler;
	initCompiler(&compiler, TYPE_SCRIPT);
	
	parser.hadError = false;
	parser.panicMode = false;
	
	advance();
	
	while (!match(TOKEN_EOF)) {
		declaration();
	}
	
	ObjFunction* function = endCompiler();
	return parser.hadError ? NULL : function;
}

/* Mark the compiler's objects as reachable. */
void markCompilerRoots() {
	Compiler* compiler = current;
	
	while (compiler != NULL) {
		markObject((Obj*)compiler->function);
		compiler = (Compiler*)(compiler->enclosing);
	}
}
