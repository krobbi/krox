#include <stdio.h>
#include <string.h>

#include "common.h"
#include "scanner.h"

typedef struct {
	const char* start;
	const char* current;
	int line;
} Scanner;

Scanner scanner;

/* Initialize the scanner to the start of source code. */
void initScanner(const char* source) {
	scanner.start = source;
	scanner.current = source;
	scanner.line = 1;
}

/* Return whether a character is an alphabetical character or an underscore. */
static bool isAlpha(char c) {
	return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_';
}

/* Return whether a character is a digit character. */
static bool isDigit(char c) {
	return c >= '0' && c <= '9';
}

/* Return whether the scanner is at the end of the source code. */
static bool isAtEnd() {
	return *scanner.current == '\0';
}

/* Advance to the next character and return the current character. */
static char advance() {
	scanner.current++;
	return scanner.current[-1];
}

/* Peek the current character without advancing. */
static char peek() {
	return *scanner.current;
}

/* Peek the next character without advancing. */
static char peekNext() {
	if (isAtEnd()) {
		return '\0';
	}
	
	return scanner.current[1];
}

/*
* Advance to the next character if it matches an expected character and return
* whether the character was matched.
*/
static bool match(char expected) {
	if (isAtEnd()) {
		return false;
	}
	
	if (*scanner.current != expected) {
		return false;
	}
	
	scanner.current++;
	return true;
}

/* Make and return a new token from its type. */
static Token makeToken(TokenType type) {
	Token token;
	token.type = type;
	token.start = scanner.start;
	token.length = (int)(scanner.current - scanner.start);
	token.line = scanner.line;
	return token;
}

/* Make and return a new error token from its message. */
static Token errorToken(const char* message) {
	Token token;
	token.type = TOKEN_ERROR;
	token.start = message;
	token.length = (int)strlen(message);
	token.line = scanner.line;
	return token;
}

/* Skip whitespace and comments. */
static void skipWhitespace() {
	for (;;) {
		char c = peek();
		
		switch (c) {
			case ' ':
			case '\r':
			case '\t':
				advance();
				break;
			case '\n':
				scanner.line++;
				advance();
				break;
			case '/':
				if (peekNext() == '/') {
					while (peek() != '\n' && !isAtEnd()) {
						advance();
					}
				} else {
					return;
				}
				
				break;
			default:
				return;
		}
	}
}

/*
* Check the remainder of the current lexeme against a keyword and return a
* keyword token type if it matches.
*/
static TokenType checkKeyword(int start, int length, const char* rest, TokenType type) {
	if (
		scanner.current - scanner.start == start + length
		&& memcmp(scanner.start + start, rest, length) == 0
	) {
		return type;
	}
	
	return TOKEN_IDENTIFIER;
}

/* Return an identifier or keyword token type from the current lexeme. */
static TokenType identifierType() {
	switch (scanner.start[0]) {
		case 'a': return checkKeyword(1, 2, "nd", TOKEN_AND);
		case 'c': return checkKeyword(1, 4, "lass", TOKEN_CLASS);
		case 'e': return checkKeyword(1, 3, "lse", TOKEN_ELSE);
		case 'f':
			if (scanner.current - scanner.start > 1) {
				switch (scanner.start[1]) {
					case 'a': return checkKeyword(2, 3, "lse", TOKEN_FALSE);
					case 'o': return checkKeyword(2, 1, "r", TOKEN_FOR);
					case 'u': return checkKeyword(2, 1, "n", TOKEN_FUN);
				}
			}
			
			break;
		case 'i': return checkKeyword(1, 1, "f", TOKEN_IF);
		case 'n': return checkKeyword(1, 2, "il", TOKEN_NIL);
		case 'o': return checkKeyword(1, 1, "r", TOKEN_OR);
		case 'p': return checkKeyword(1, 4, "rint", TOKEN_PRINT);
		case 'r': return checkKeyword(1, 5, "eturn", TOKEN_RETURN);
		case 's': return checkKeyword(1, 4, "uper", TOKEN_SUPER);
		case 't':
			if (scanner.current - scanner.start > 1) {
				switch(scanner.start[1]) {
					case 'h': return checkKeyword(2, 2, "is", TOKEN_THIS);
					case 'r': return checkKeyword(2, 2, "ue", TOKEN_TRUE);
				}
			}
			
			break;
		case 'v': return checkKeyword(1, 2, "ar", TOKEN_VAR);
		case 'w': return checkKeyword(1, 4, "hile", TOKEN_WHILE);
	}
	
	return TOKEN_IDENTIFIER;
}

/* Scan and return an identifier token. */
static Token identifier() {
	while (isAlpha(peek()) || isDigit(peek())) {
		advance();
	}
	
	return makeToken(identifierType());
}

/* Scan and return a number token. */
static Token number() {
	while (isDigit(peek())) {
		advance();
	}
	
	/* Look for a fractional part. */
	if (peek() == '.' && isDigit(peekNext())) {
		/* Consume the decimal point. */
		advance();
		
		while (isDigit(peek())) {
			advance();
		}
	}
	
	return makeToken(TOKEN_NUMBER);
}

/* Scan and return a string token. */
static Token string() {
	while (peek() != '"' && !isAtEnd()) {
		if (peek() == '\n') {
			scanner.line++;
		}
		
		advance();
	}
	
	if(isAtEnd()){
		return errorToken("Unterminated string.");
	}
	
	/* Consume the closing quote. */
	advance();
	return makeToken(TOKEN_STRING);
}

/* Scan and return the next token from the scanner. */
Token scanToken() {
	skipWhitespace();
	scanner.start = scanner.current;
	
	if (isAtEnd()) {
		return makeToken(TOKEN_EOF);
	}
	
	char c = advance();
	
	if (isAlpha(c)) {
		return identifier();
	}
	
	if (isDigit(c)) {
		return number();
	}
	
	switch (c) {
		case '(': return makeToken(TOKEN_LEFT_PAREN);
		case ')': return makeToken(TOKEN_RIGHT_PAREN);
		case '{': return makeToken(TOKEN_LEFT_BRACE);
		case '}': return makeToken(TOKEN_RIGHT_BRACE);
		case ';': return makeToken(TOKEN_SEMICOLON);
		case ',': return makeToken(TOKEN_COMMA);
		case '.': return makeToken(TOKEN_DOT);
		case '-': return makeToken(TOKEN_MINUS);
		case '+': return makeToken(TOKEN_PLUS);
		case '/': return makeToken(TOKEN_SLASH);
		case '*': return makeToken(TOKEN_STAR);
		case '!': return makeToken(match('=') ? TOKEN_BANG_EQUAL : TOKEN_BANG);
		case '=': return makeToken(match('=') ? TOKEN_EQUAL_EQUAL : TOKEN_EQUAL);
		case '<': return makeToken(match('=') ? TOKEN_LESS_EQUAL : TOKEN_LESS);
		case '>': return makeToken(match('=') ? TOKEN_GREATER_EQUAL : TOKEN_GREATER);
		case '"': return string();
	}
	
	return errorToken("Unexpected character.");
}
