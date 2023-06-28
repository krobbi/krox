#ifndef clox_intrinsic_h
#define clox_intrinsic_h

#include "object.h"

typedef void (*DefineNativeFn)(const char* name, NativeFn function);

void initIntrinsics(int argc, char** argv);
void installIntrinsics(DefineNativeFn defineNative);

#endif
