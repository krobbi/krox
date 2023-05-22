#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "object.h"
#include "memory.h"
#include "value.h"

/* Return whether two values are equal. */
bool valuesEqual(Value a, Value b) {
#ifdef NAN_BOXING
	if (IS_NUMBER(a) && IS_NUMBER(b)){
		return AS_NUMBER(a) == AS_NUMBER(b);
	}
	
	return a == b;
#else /* Not NaN boxing. */
	if(a.type != b.type) {
		return false;
	}
	
	switch (a.type) {
		case VAL_BOOL:   return AS_BOOL(a) == AS_BOOL(b);
		case VAL_NIL:    return true;
		case VAL_NUMBER: return AS_NUMBER(a) == AS_NUMBER(b);
		case VAL_OBJ:    return AS_OBJ(a) == AS_OBJ(b);
		default:         return false; /* Unreachable. */
	}
#endif /* End NaN boxing. */
}

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

/* Pretty print a double value. */
static void printDouble(double value) {
	char string[64] = {0};
	sprintf(string, "%f", value);
	
	/* Panic if `sprintf` overflowed. */
	if (string[63] != '\0') {
		exit(70);
	}
	
	char* point = strchr(string, '.');
	
	/* If we have a decimal point. */
	if (point != NULL) {
		char* tail = strchr(string, '\0') - 1;
		
		/* Strip trailing `0`s. */
		while (tail > point && *tail == '0') {
			*tail = '\0';
			tail--;
		}
		
		/* Strip decimal point if there is no fractional part. */
		if (tail == point) {
			*point = '\0';
		}
	}
	
	/* Never display `-0`. */
	if (strcmp(string, "-0") == 0) {
		printf("0");
	} else {
		printf(string);
	}
}

/* Print a value. */
void printValue(Value value) {
#ifdef NAN_BOXING
	if (IS_BOOL(value)) {
		printf(AS_BOOL(value) ? "true" : "false");
	} else if (IS_NIL(value)) {
		printf("nil");
	} else if (IS_NUMBER(value)) {
		printDouble(AS_NUMBER(value));
	} else if (IS_OBJ(value)) {
		printObject(value);
	}
#else /* Not NaN boxing. */
	switch (value.type) {
		case VAL_BOOL:   printf(AS_BOOL(value) ? "true" : "false"); break;
		case VAL_NIL:    printf("nil"); break;
		case VAL_NUMBER: printDouble(AS_NUMBER(value)); break;
		case VAL_OBJ:    printObject(value); break;
	}
#endif /* End NaN boxing. */
}
