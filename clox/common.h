#ifndef clox_common_h
#define clox_common_h

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Optional memory optimizations. */
#define NAN_BOXING
#define CONSTANT_MERGING

/* Debug flags. */
#define DEBUG_PRINT_CODE
#define DEBUG_TRACE_EXECUTION
#define DEBUG_STRESS_GC
#define DEBUG_LOG_GC

/* Disable debug flags. */
#undef DEBUG_PRINT_CODE
#undef DEBUG_TRACE_EXECUTION
#undef DEBUG_STRESS_GC
#undef DEBUG_LOG_GC

#define UINT8_COUNT (UINT8_MAX + 1)

#endif
