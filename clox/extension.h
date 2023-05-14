#ifndef clox_extension_h
#define clox_extension_h

#include "object.h"

typedef void (*DefineNativeFn)(const char* name, NativeFn function);

void initExtensions(int argc, char** argv);
void freeExtensions();
void installExtensions(DefineNativeFn defineNative);

#endif
