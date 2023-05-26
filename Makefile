# Bootstrap Krox for Windows. Currently unfinished.

# C compiler:
C_COMPILER := gcc
C_COMPILER_FLAGS := -O2 -Wall -Werror -Wextra -Wno-unused-parameter -flto -std=c99

# Clox:
CLOX_SOURCES_DIR := clox
CLOX_OBJECTS_DIR := $(CLOX_SOURCES_DIR)\obj
CLOX_HEADERS := $(wildcard $(CLOX_SOURCES_DIR)/*.h)
CLOX_SOURCES := $(wildcard $(CLOX_SOURCES_DIR)/*.c)
CLOX_OBJECTS := $(addprefix $(CLOX_OBJECTS_DIR)/, $(notdir $(CLOX_SOURCES:.c=.o)))
CLOX_EXECUTABLE := lox.exe

# LoxKrox:
LOXKROX_DIR := loxkrox
LOXKROX_GENERATOR := $(LOXKROX_DIR)\generator.lox
LOXKROX_SOURCE := $(LOXKROX_DIR)\krox.lox

# Bootstrap Krox:
.PHONY: all
all: $(LOXKROX_SOURCE)
	$(CLOX_EXECUTABLE) $(LOXKROX_SOURCE)

# Clean all build output:
.PHONY: clean
clean:
	if exist "$(LOXKROX_SOURCE)" del /f /q "$(LOXKROX_SOURCE)"
	if exist "$(CLOX_EXECUTABLE)" del /f /q "$(CLOX_EXECUTABLE)"
	if exist "$(CLOX_OBJECTS_DIR)" rd /s /q "$(CLOX_OBJECTS_DIR)"

# Regenerate LoxKrox source:
.PHONY: regen
regen: $(CLOX_EXECUTABLE)
	$(CLOX_EXECUTABLE) $(LOXKROX_GENERATOR)

# Generate LoxKrox source:
$(LOXKROX_SOURCE): $(CLOX_EXECUTABLE)
	$(CLOX_EXECUTABLE) $(LOXKROX_GENERATOR)

# Link clox executable:
$(CLOX_EXECUTABLE): $(CLOX_OBJECTS) | $(CLOX_OBJECTS_DIR)
	$(C_COMPILER) $(C_COMPILER_FLAGS) $^ -o $@

# Compile clox objects:
$(CLOX_OBJECTS_DIR)/%.o: $(CLOX_SOURCES_DIR)/%.c $(CLOX_HEADERS) | $(CLOX_OBJECTS_DIR)
	$(C_COMPILER) $(C_COMPILER_FLAGS) -c $< -o $@

# Make clox objects directory:
$(CLOX_OBJECTS_DIR):
	mkdir "$(CLOX_OBJECTS_DIR)"
