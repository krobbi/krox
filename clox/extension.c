#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "extension.h"

/* Stream IDs. */
#define STREAM_STDIN  0
#define STREAM_STDOUT 1
#define STREAM_STDERR 2
#define STREAM_MAX    7

static int loxArgCount = 0;
static char** loxArgs = NULL;
static int* loxArgLengths = NULL;
static FILE* loxStreams[] = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL};

/* The arg extension. */
static Value argExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	int index = (int)AS_NUMBER(args[0]);
	
	if (index < 0 || index >= loxArgCount) {
		return NIL_VAL; /* Argument index out of range. */
	}
	
	return OBJ_VAL(takeString(loxArgs[index], loxArgLengths[index]));
}

/* The args extension. */
static Value argsExtension(int argCount, Value* args) {
	return NUMBER_VAL((double)loxArgCount);
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
	defineNative("put", putExtension);
	defineNative("stderr", stderrExtension);
	defineNative("stdin", stdinExtension);
	defineNative("stdout", stdoutExtension);
}
