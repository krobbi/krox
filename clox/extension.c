#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "extension.h"

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
	
	return OBJ_VAL(takeString(loxArgs[index], loxArgLengths[index]));
}

/* The args extension. */
static Value argsExtension(int argCount, Value* args) {
	return NUMBER_VAL((double)loxArgCount);
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
	defineNative("close", closeExtension);
	defineNative("get", getExtension);
	defineNative("put", putExtension);
	defineNative("read", readExtension);
	defineNative("stderr", stderrExtension);
	defineNative("stdin", stdinExtension);
	defineNative("stdout", stdoutExtension);
	defineNative("write", writeExtension);
}
