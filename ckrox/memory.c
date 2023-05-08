#include <stdlib.h>

#include "memory.h"
#include "vm.h"

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

/* Free an object. */
static void freeObject(Obj* object) {
	switch (object->type) {
		case OBJ_FUNCTION: {
			ObjFunction* function = (ObjFunction*)object;
			freeChunk(&function->chunk);
			FREE(ObjFunction, object);
			break;
		}
		case OBJ_NATIVE: {
			FREE(ObjNative, object);
			break;
		}
		case OBJ_STRING: {
			ObjString* string = (ObjString*)object;
			FREE_ARRAY(char, string->chars, string->length);
			FREE(ObjString, object);
			break;
		}
	}
}

/* Free the VM's objects. */
void freeObjects() {
	Obj* object = vm.objects;
	
	while (object != NULL) {
		Obj* next = object->next;
		freeObject(object);
		object = next;
	}
}
