#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "intrinsic.h"
#include "memory.h"

/* Stream IDs. */
#define STREAM_STDIN  0
#define STREAM_STDOUT 1
#define STREAM_STDERR 2
#define STREAM_FILES  3
#define STREAM_MAX    7

static int loxArgc = 0;
static char** loxArgv = NULL;
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

/* The argc intrinsic. */
static Value argcIntrinsic(int argCount, Value* args) {
	return NUMBER_VAL((double)loxArgc);
}

/* The argv intrinsic. */
static Value argvIntrinsic(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return NIL_VAL; /* Invalid arguments. */
	}
	
	int index = (int)AS_NUMBER(args[0]);
	
	if (index < 0 || index >= loxArgc) {
		return NIL_VAL; /* Argument index out of range. */
	}
	
	char* arg = loxArgv[index];
	return OBJ_VAL(copyString(arg, strlen(arg)));
}

/* The chr intrinsic. */
static Value chrIntrinsic(int argCount, Value* args) {
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

/* The close intrinsic. */
static Value closeIntrinsic(int argCount, Value* args) {
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

/* The get intrinsic. */
static Value getIntrinsic(int argCount, Value* args) {
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

/* The length intrinsic. */
static Value lengthIntrinsic(int argCount, Value* args) {
	if (argCount != 1 || !IS_STRING(args[0])) {
		return NUMBER_VAL(0.0); /* Invalid arguments. */
	}
	
	return NUMBER_VAL((double)(AS_STRING(args[0])->length));
}

/* The ord intrinsic. */
static Value ordIntrinsic(int argCount, Value* args) {
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

/* The put intrinsic. */
static Value putIntrinsic(int argCount, Value* args) {
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

/* The read intrinsic. */
static Value readIntrinsic(int argCount, Value* args) {
	return openFileHandle(argCount, args, "rb");
}

/* The stderr intrinsic. */
static Value stderrIntrinsic(int argCount, Value* args) {
	return NUMBER_VAL((double)STREAM_STDERR);
}

/* The stdin intrinsic. */
static Value stdinIntrinsic(int argCount, Value* args) {
	return NUMBER_VAL((double)STREAM_STDIN);
}

/* The stdout intrinsic. */
static Value stdoutIntrinsic(int argCount, Value* args) {
	return NUMBER_VAL((double)STREAM_STDOUT);
}

/* The substring intrinsic. */
static Value substringIntrinsic(int argCount, Value* args) {
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

/* The trunc intrinsic. */
static Value truncIntrinsic(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return NUMBER_VAL(0.0); /* Invalid arguments. */
	}
	
	return NUMBER_VAL(trunc(AS_NUMBER(args[0])));
}

/* The write intrinsic. */
static Value writeIntrinsic(int argCount, Value* args) {
	return openFileHandle(argCount, args, "wb");
}

/* Initialize the intrinsics. */
void initIntrinsics(int argc, char** argv) {
	if (argc > 1) {
		loxArgc = argc - 1;
		loxArgv = &argv[1];
	}
	
	/* Populate standard streams. */
	loxStreams[STREAM_STDIN]  = stdin;
	loxStreams[STREAM_STDOUT] = stdout;
	loxStreams[STREAM_STDERR] = stderr;
}

/* Install the intrinsics. */
void installIntrinsics(DefineNativeFn defineNative) {
	defineNative("_argc", argcIntrinsic);
	defineNative("_argv", argvIntrinsic);
	defineNative("_chr", chrIntrinsic);
	defineNative("_close", closeIntrinsic);
	defineNative("_get", getIntrinsic);
	defineNative("_length", lengthIntrinsic);
	defineNative("_ord", ordIntrinsic);
	defineNative("_put", putIntrinsic);
	defineNative("_read", readIntrinsic);
	defineNative("_stderr", stderrIntrinsic);
	defineNative("_stdin", stdinIntrinsic);
	defineNative("_stdout", stdoutIntrinsic);
	defineNative("_substring", substringIntrinsic);
	defineNative("_trunc", truncIntrinsic);
	defineNative("_write", writeIntrinsic);
}
