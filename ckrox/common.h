#ifndef ckrox_common_h
#define ckrox_common_h

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Debug flags. */
#define DEBUG_PRINT_CODE
#define DEBUG_TRACE_EXECUTION

/* Disable debug flags. */
#undef DEBUG_PRINT_CODE
#undef DEBUG_TRACE_EXECUTION

#define UINT8_COUNT (UINT8_MAX + 1)

#endif
