# Bootstrap Krox for Windows through clox. Currently a hello world.

# Compiler settings:
CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -Werror

# Suppressed warnings:
CFLAGS += -Wno-unused-parameter

# Debug and release mode compiler flags:
ifeq ($(MODE), debug)
	CFLAGS += -Og -DDEBUG -g
else
	CFLAGS += -O2 -flto
endif

# Directories:
CLOX_SOURCE_DIR = clox
CLOX_OBJECTS_DIR = obj

LOXKROX_SOURCE_DIR = loxkrox

# Files:
CLOX_HEADERS = $(wildcard $(CLOX_SOURCE_DIR)/*.h)
CLOX_SOURCES = $(wildcard $(CLOX_SOURCE_DIR)/*.c)
CLOX_OBJECTS = $(addprefix $(CLOX_OBJECTS_DIR)/, $(notdir $(CLOX_SOURCES:.c=.o)))
CLOX_EXECUTABLE = lox.exe

LOXKROX_SOURCE = $(LOXKROX_SOURCE_DIR)/krox.lox

# Subcommands:
.PHONY: build clean

# Build clox executable and run LoxKrox:
build: $(CLOX_EXECUTABLE)
	$(CLOX_EXECUTABLE) $(LOXKROX_SOURCE)

# Clean all build output:
clean:
	if exist $(CLOX_OBJECTS_DIR) rd /s /q $(CLOX_OBJECTS_DIR)
	if exist $(CLOX_EXECUTABLE) del /f /q $(CLOX_EXECUTABLE)

# Link clox executable:
$(CLOX_EXECUTABLE): $(CLOX_OBJECTS) | $(CLOX_OBJECTS_DIR)
	$(CC) $(CFLAGS) $^ -o $@

# Compile clox objects:
$(CLOX_OBJECTS_DIR)/%.o: $(CLOX_SOURCE_DIR)/%.c $(CLOX_HEADERS) | $(CLOX_OBJECTS_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Make clox objects directory:
$(CLOX_OBJECTS_DIR):
	mkdir $(CLOX_OBJECTS_DIR)
