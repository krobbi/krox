#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "extension.h"
#include "memory.h"

/* Stream IDs. */
#define STREAM_STDIN  0
#define STREAM_STDOUT 1
#define STREAM_STDERR 2
#define STREAM_FILES  3
#define STREAM_MAX    7

static int loxArgCount = 0;
static char** loxArgs = NULL;
static int* loxArgLengths = NULL;
static FILE* loxStreams[] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL};

/* Open and return a new file handle from arguments and a mode. */
static Value openFileHandle(int argCount, Value* args, const char* mode) {
	if (argCount != 1 || !IS_STRING(args[0])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	for (int handle = STREAM_FILES; handle <= STREAM_MAX; handle++) {
		if (loxStreams[handle] != NULL) {
			continue; /* File handle already in use. */
		}
		
		FILE* stream = fopen(AS_CSTRING(args[0]), mode);
		
		if (stream == NULL) {
			return NIL_VAL; /* Failed to open file handle. */
		}
		
		loxStreams[handle] = stream;
		return NUMBER_VAL((double)handle);
	}
	
	return NIL_VAL; /* No file handles available. */
}

/* The arg extension. */
static Value argExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	int index = (int)AS_NUMBER(args[0]);
	
	if (index < 0 || index >= loxArgCount) {
		return NIL_VAL; /* Argument index out of range. */
	}
	
	return OBJ_VAL(copyString(loxArgs[index], loxArgLengths[index]));
}

/* The args extension. */
static Value argsExtension(int argCount, Value* args) {
	return NUMBER_VAL((double)loxArgCount);
}

/* The chr extension. */
static Value chrExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	int code = (int)AS_NUMBER(args[0]);
	
	if (code < 0 || code > 255) {
		return NIL_VAL; /* Not an ASCII character. */
	}
	
	char* chars = ALLOCATE(char, 2);
	chars[0] = (char)code;
	chars[1] = '\0';
	return OBJ_VAL(takeString(chars, 1));
}

/* The close extension. */
static Value closeExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return BOOL_VAL(false); /* Invalid arguments. */
	}
	
	int handle = (int)AS_NUMBER(args[0]);
	
	if (handle < STREAM_FILES || handle > STREAM_MAX) {
		return BOOL_VAL(false); /* Not a file handle. */
	}
	
	FILE* stream = loxStreams[handle];
	
	if (stream == NULL) {
		return BOOL_VAL(false); /* File already closed. */
	}
	
	int result = fclose(stream);
	
	if (result == EOF) {
		return BOOL_VAL(false); /* Failed to close file. */
	}
	
	loxStreams[handle] = NULL;
	return BOOL_VAL(true);
}

/* The get extension. */
static Value getExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	int handle = (int)AS_NUMBER(args[0]);
	
	if (handle < 0 || handle > STREAM_MAX) {
		return NIL_VAL; /* Invalid file handle. */
	}
	
	FILE* stream = loxStreams[handle];
	
	if (stream == NULL) {
		return NIL_VAL; /* Unopened stream. */
	}
	
	int result = fgetc(stream);
	
	if (result == EOF) {
		return NIL_VAL; /* End of file or error. */
	}
	
	return NUMBER_VAL((double)result);
}

/* The length extension. */
static Value lengthExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_STRING(args[0])) {
		return NUMBER_VAL(0.0); /* Invalid arguments. */
	}
	
	return NUMBER_VAL((double)(AS_STRING(args[0])->length));
}

/* The ord extension. */
static Value ordExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_STRING(args[0])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	ObjString* string = AS_STRING(args[0]);
	
	if (string->length != 1) {
		return NIL_VAL; /* Not a single character. */
	}
	
	int value = (int)(string->chars[0]);
	
	if (value < 0 || value > 255) {
		return NIL_VAL; /* Not an ASCII character. */
	}
	
	return NUMBER_VAL((double)value);
}

/* The put extension. */
static Value putExtension(int argCount, Value* args) {
	if (argCount != 2 || !IS_NUMBER(args[0]) || !IS_NUMBER(args[1])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	int byte = (int)AS_NUMBER(args[0]);
	
	if (byte < 0 || byte > 255) {
		return NIL_VAL; /* Invalid byte. */
	}
	
	int handle = (int)AS_NUMBER(args[1]);
	
	if (handle < 0 || handle > STREAM_MAX) {
		return NIL_VAL; /* Invalid file handle. */
	}
	
	FILE* stream = loxStreams[handle];
	
	if (stream == NULL) {
		return NIL_VAL; /* Unopened stream. */
	}
	
	int result = fputc(byte, stream);
	
	if (result == EOF) {
		return NIL_VAL; /* Failed to put byte. */
	}
	
	return NUMBER_VAL((double)byte);
}

/* The read extension. */
static Value readExtension(int argCount, Value* args) {
	return openFileHandle(argCount, args, "rb");
}

/* The stderr extension. */
static Value stderrExtension(int argCount, Value* args) {
	return NUMBER_VAL((double)STREAM_STDERR);
}

/* The stdin extension. */
static Value stdinExtension(int argCount, Value* args) {
	return NUMBER_VAL((double)STREAM_STDIN);
}

/* The stdout extension. */
static Value stdoutExtension(int argCount, Value* args) {
	return NUMBER_VAL((double)STREAM_STDOUT);
}

/* The substring extension. */
static Value substringExtension(int argCount, Value* args) {
	if (argCount != 3 || !IS_STRING(args[0]) || !IS_NUMBER(args[1]) || !IS_NUMBER(args[2]))	{
		return NIL_VAL; /* Invalid arguments. */
	}
	
	ObjString* string = AS_STRING(args[0]);
	int start = (int)AS_NUMBER(args[1]);
	int length = (int)AS_NUMBER(args[2]);
	
	if (start < 0 || length < 0 || start + length > string->length) {
		return NIL_VAL; /* Substring out of bounds. */
	}
	
	if (length == string->length) {
		return args[0]; /* Special case for same length substring. */
	}
	
	return OBJ_VAL(copyString(string->chars + start, length));
}

/* The write extension. */
static Value writeExtension(int argCount, Value* args) {
	return openFileHandle(argCount, args, "wb");
}

/* Initialize the extensions. */
void initExtensions(int argc, char** argv) {
	loxArgCount = argc - 1;
	loxArgs = argv + 1;
	
	/* Cache argument lengths. */
	if (loxArgCount > 0) {
		loxArgLengths = (int*)malloc(sizeof(int) * loxArgCount);
		
		for (int i = 0; i < loxArgCount; i++) {
			loxArgLengths[i] = strlen(loxArgs[i]);
		}
	} else if (loxArgCount < 0) {
		loxArgCount = 0; /* Probably unreachable. Makes argc extension safer. */
	}
	
	/* Populate standard streams. */
	loxStreams[STREAM_STDIN]  = stdin;
	loxStreams[STREAM_STDOUT] = stdout;
	loxStreams[STREAM_STDERR] = stderr;
}

/* Free the extensions. */
void freeExtensions() {
	if (loxArgCount > 0) {
		free(loxArgLengths);
	}
}

/* Install the extensions. */
void installExtensions(DefineNativeFn defineNative) {
	defineNative("arg", argExtension);
	defineNative("args", argsExtension);
	defineNative("chr", chrExtension);
	defineNative("close", closeExtension);
	defineNative("get", getExtension);
	defineNative("length", lengthExtension);
	defineNative("ord", ordExtension);
	defineNative("put", putExtension);
	defineNative("read", readExtension);
	defineNative("stderr", stderrExtension);
	defineNative("stdin", stdinExtension);
	defineNative("stdout", stdoutExtension);
	defineNative("substring", substringExtension);
	defineNative("write", writeExtension);
}
