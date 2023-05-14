#include <stdlib.h>
#include <string.h>

#include "extension.h"

static int loxArgCount = 0;
static char** loxArgs = NULL;
static int* loxArgLengths = NULL;

/* The argc extension. */
static Value argcExtension(int argCount, Value* args) {
	return NUMBER_VAL((double)loxArgCount);
}

/* The argv extension. */
static Value argvExtension(int argCount, Value* args) {
	if (argCount != 1 || !IS_NUMBER(args[0])) {
		return NIL_VAL;
	}
	
	int index = (int)AS_NUMBER(args[0]);
	
	if (index < 0 || index >= loxArgCount) {
		return NIL_VAL;
	}
	
	return OBJ_VAL(takeString(loxArgs[index], loxArgLengths[index]));
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
}

/* Free the extensions. */
void freeExtensions() {
	if (loxArgCount > 0) {
		free(loxArgLengths);
	}
}

/* Install the extensions. */
void installExtensions(DefineNativeFn defineNative) {
	defineNative("argc", argcExtension);
	defineNative("argv", argvExtension);
}
