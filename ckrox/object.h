#ifndef ckrox_object_h
#define ckrox_object_h

#include "common.h"
#include "value.h"

/* Return the object type of a value. */
#define OBJ_TYPE(value) (AS_OBJ(value)->type)

/* Check object types. */
#define IS_STRING(value) isObjType(value, OBJ_STRING)

/* Cast objects to types. */
#define AS_STRING(value)  ((ObjString*)AS_OBJ(value))
#define AS_CSTRING(value) (((ObjString*)AS_OBJ(value))->chars)

typedef enum {
	OBJ_STRING,
} ObjType;

struct Obj {
	ObjType type;
	struct Obj* next;
};

struct ObjString {
	Obj obj;
	int length;
	char* chars;
	uint32_t hash;
};

ObjString* takeString(char* chars, int length);
ObjString* copyString(const char* chars, int length);
void printObject(Value value);

/* Return whether a value is an object and matches a type. */
static inline bool isObjType(Value value, ObjType type) {
	return IS_OBJ(value) && AS_OBJ(value)->type == type;
}

#endif
