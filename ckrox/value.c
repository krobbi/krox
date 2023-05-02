#include <stdio.h>

#include "memory.h"
#include "value.h"

/* Initialize a value array to an empty state. */
void initValueArray(ValueArray* array) {
	array->values = NULL;
	array->capacity = 0;
	array->count = 0;
}

/* Write a value to a value array. */
void writeValueArray(ValueArray* array, Value value) {
	if (array->capacity < array->count + 1) {
		int oldCapacity = array->capacity;
		array->capacity = GROW_CAPACITY(oldCapacity);
		array->values = GROW_ARRAY(Value, array->values, oldCapacity, array->capacity);
	}
	
	array->values[array->count] = value;
	array->count++;
}

/* Free a value array. */
void freeValueArray(ValueArray* array) {
	FREE_ARRAY(Value, array->values, array->capacity);
	initValueArray(array);
}

/* Print a value. */
void printValue(Value value) {
	printf("%g", value);
}
