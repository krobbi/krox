#include <stdlib.h>
#include <string.h>

#include "memory.h"
#include "object.h"
#include "value.h"
#include "table.h"

/* The maximum fraction of a table that can be set before rehashing. */
#define TABLE_MAX_LOAD 0.75

/* Initialize a table to an empty state. */
void initTable(Table* table) {
	table->count = 0;
	table->capacity = 0;
	table->entries = NULL;
}

/* Free a table's entries. */
void freeTable(Table* table) {
	FREE_ARRAY(Entry, table->entries, table->capacity);
	initTable(table);
}

/* Find an entry from its key. */
static Entry* findEntry(Entry* entries, int capacity, ObjString* key) {
	uint32_t index = key->hash % capacity;
	Entry* tombstone = NULL;
	
	for (;;) {
		Entry* entry = &entries[index];
		
		if (entry->key == NULL) {
			/* We've encountered either an empty entry or a tombstone. */
			
			if (IS_NIL(entry->value)) {
				/*
				* We've found an empty entry. Either return it or reuse a
				* tombstone.
				*/
				return tombstone != NULL ? tombstone : entry;
			} else {
				/*
				* We've found a tombstone. Mark it for potential reuse if we
				* haven't found one already.
				*/
				if (tombstone != NULL) {
					tombstone = entry;
				}
			}
		} else if (entry->key == key) {
			/*
			* We've found the entry, so we can return it. We are checking the
			* keys by address, but this should not be a problem due to string
			* interning. (String objects are immutable and each unique string in
			* the VM's world is deduplicated and shares an address.)
			*/
			return entry;
		}
		
		index = (index + 1) % capacity;
	}
}

/* Adjust a table's capacity and rehash it. */
static void adjustCapacity(Table* table, int capacity) {
	Entry* entries = ALLOCATE(Entry, capacity);
	
	for (int i = 0; i < capacity; i++) {
		entries[i].key = NULL;
		entries[i].value = NIL_VAL;
	}
	
	/* Rehashing flushes tombstones, so we need to recalculate the count. */
	table->count = 0;
	
	for (int i = 0; i < table->capacity; i++) {
		Entry* entry = &table->entries[i];
		
		if (entry->key == NULL) {
			continue;
		}
		
		Entry* dest = findEntry(entries, capacity, entry->key);
		dest->key = entry->key;
		dest->value = entry->value;
		table->count++;
	}
	
	FREE_ARRAY(Entry, table->entries, table->capacity);
	table->entries = entries;
	table->capacity = capacity;
}

/*
* Get a value from a table from its key and return whether an entry exists. If
* an entry does exist, output its value at a value pointer.
*/
bool tableGet(Table* table, ObjString* key, Value* value) {
	if (table->count == 0) {
		return false;
	}
	
	Entry* entry = findEntry(table->entries, table->capacity, key);
	
	if (entry->key == NULL) {
		return false;
	}
	
	*value = entry->value;
	return true;
}

/*
* Set a table entry from its key and value and return whether a new key was
* added.
*/
bool tableSet(Table* table, ObjString* key, Value value) {
	if (table->count + 1 > table->capacity * TABLE_MAX_LOAD) {
		int capacity = GROW_CAPACITY(table->capacity);
		adjustCapacity(table, capacity);
	}
	
	Entry* entry = findEntry(table->entries, table->capacity, key);
	bool isNewKey = entry->key == NULL;
	
	/* Only increase the table's count if we're not replacing a tombstone. */
	if (isNewKey && IS_NIL(entry->value)) {
		table->count++;
	}
	
	entry->key = key;
	entry->value = value;
	return isNewKey;
}

/*
* Delete an entry from a table from its key and return whether the entry
* existed.
*/
bool tableDelete(Table* table, ObjString* key) {
	if (table->count == 0) {
		return false;
	}
	
	Entry* entry = findEntry(table->entries, table->capacity, key);
	
	if (entry->key == NULL) {
		return false;
	}
	
	/* Mark the entry with a tombstone. */
	entry->key = NULL;
	entry->value = BOOL_VAL(true);
	return true;
}

/* Set all entries from a source table to a target table. */
void tableAddAll(Table* from, Table* to) {
	for (int i = 0; i < from->capacity; i++) {
		Entry* entry = &from->entries[i];
		
		if (entry->key != NULL) {
			tableSet(to, entry->key, entry->value);
		}
	}
}

/*
* Find and return a string key from a table. Return null if the key does not
* exist.
*/
ObjString* tableFindString(Table* table, const char* chars, int length, uint32_t hash) {
	if (table->count == 0) {
		return NULL;
	}
	
	uint32_t index = hash % table->capacity;
	
	for (;;) {
		Entry* entry = &table->entries[index];
		
		if (entry -> key == NULL) {
			/*
			* We've either hit an empty entry or a tombstone. If it is not a
			* tombstone, the key does not exist.
			*/
			if (IS_NIL(entry->value)) {
				return NULL;
			}
		} else if (
			entry->key->length == length && entry->key->hash == hash
			&& memcmp(entry->key->chars, chars, length) == 0
		) {
			/*
			* We've hit an entry with a matching hash, but we still need to
			* check the key's value in case of collision.
			*/
			return entry->key;
		}
		
		index = (index + 1) % table->capacity;
	}
}

/* Remove unreachable keys from a table. */
void tableRemoveWhite(Table* table) {
	for (int i = 0; i < table->capacity; i++) {
		Entry* entry = &table->entries[i];
		
		if (entry->key != NULL && !entry->key->obj.isMarked) {
			tableDelete(table, entry->key);
		}
	}
}

/* Mark a table's values as reachable. */
void markTable(Table* table) {
	for (int i = 0; i < table->capacity; i++) {
		Entry* entry = &table->entries[i];
		markObject((Obj*)entry->key);
		markValue(entry->value);
	}
}
