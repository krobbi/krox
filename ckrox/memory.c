#include <stdlib.h>

#include "memory.h"

/* Reallocate or free a pointed block of memory to a new size. */
void* reallocate(void* pointer, size_t oldSize, size_t newSize) {
	if(newSize == 0){
		free(pointer);
		return NULL;
	}
	
	void* result = realloc(pointer, newSize);
	
	/* Exit if allocation failed. */
	if(result == NULL) {
		exit(1);
	}
	
	return result;
}
