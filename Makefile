# Build CKrox for Windows.
# Usage:
# `make [build]` - Build krox.exe. Include `MODE=release` for release mode.
# `make run` - Build and run krox.exe. Include `MODE=release` for release mode.
# `make clean` - Clean all build output.

# Compiler settings:
CC = gcc
CFLAGS = -std=c99 -Wall -Wextra -Werror

# Suppressed warnings:
CFLAGS += -Wno-unused-parameter

# Release and debug mode compiler flags:
ifeq ($(MODE), release)
	CFLAGS += -O2 -flto
else
	CFLAGS += -O0 -DDEBUG -g
endif

# Directories:
SOURCE_DIR = ckrox
OBJECTS_DIR = obj

# Files:
HEADERS = $(wildcard $(SOURCE_DIR)/*.h)
SOURCES = $(wildcard $(SOURCE_DIR)/*.c)
OBJECTS = $(addprefix $(OBJECTS_DIR)/, $(notdir $(SOURCES:.c=.o)))
EXECUTABLE = krox.exe

# Subcommands:
.PHONY: build run clean

# Build executable:
build: $(EXECUTABLE)

# Build and run executable:
run: $(EXECUTABLE)
	$(EXECUTABLE)

# Clean all build output:
clean:
	if exist $(OBJECTS_DIR) rd /s /q $(OBJECTS_DIR)
	if exist $(EXECUTABLE) del /f /q $(EXECUTABLE)

# Link executable:
$(EXECUTABLE): $(OBJECTS) | $(OBJECTS_DIR)
	$(CC) $(CFLAGS) $^ -o $@

# Compile objects:
$(OBJECTS_DIR)/%.o: $(SOURCE_DIR)/%.c $(HEADERS) | $(OBJECTS_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Make objects directory:
$(OBJECTS_DIR):
	mkdir $(OBJECTS_DIR)
