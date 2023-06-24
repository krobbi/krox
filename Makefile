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
CLOX := lox.exe

# LoxKrox:
LOXKROX_DIR := loxkrox
LOXKROX_GENERATOR := $(LOXKROX_DIR)\generator.lox
LOXKROX := $(LOXKROX_DIR)\krox.lox

# Bootstrap Krox:
.PHONY: all
all: $(LOXKROX)
	$(CLOX) $(LOXKROX)

# Clean all build output:
.PHONY: clean
clean:
	if exist "$(LOXKROX)" del /f /q "$(LOXKROX)"
	if exist "$(CLOX)" del /f /q "$(CLOX)"
	if exist "$(CLOX_OBJECTS_DIR)" rd /s /q "$(CLOX_OBJECTS_DIR)"

# Regenerate LoxKrox:
.PHONY: regen
regen: $(CLOX)
	$(CLOX) $(LOXKROX_GENERATOR)

# Regenerate LoxKrox in debug mode:
.PHONY: regen-debug
regen-debug: $(CLOX)
	$(CLOX) $(LOXKROX_GENERATOR) --debug

# Generate LoxKrox:
$(LOXKROX): $(CLOX)
	$(CLOX) $(LOXKROX_GENERATOR)

# Link clox:
$(CLOX): $(CLOX_OBJECTS) | $(CLOX_OBJECTS_DIR)
	$(C_COMPILER) $(C_COMPILER_FLAGS) $^ -o $@

# Compile clox objects:
$(CLOX_OBJECTS_DIR)/%.o: $(CLOX_SOURCES_DIR)/%.c $(CLOX_HEADERS) | $(CLOX_OBJECTS_DIR)
	$(C_COMPILER) $(C_COMPILER_FLAGS) -c $< -o $@

# Make clox objects directory:
$(CLOX_OBJECTS_DIR):
	mkdir "$(CLOX_OBJECTS_DIR)"
