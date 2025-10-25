#!/usr/bin/env bash

set -e

SCRIPT_PATH="$(realpath -s "$0")"
SOURCE_DIR="$(dirname "$SCRIPT_PATH")/../src"

cd "$SOURCE_DIR" || return 1

PROJECT_DIR="${SOURCE_DIR}/.."

YAML_GENERATOR_SCRIPT="$SOURCE_DIR/generate_from_yaml.py"
DEFINITIONS_DIR="$PROJECT_DIR/definitions"
FIXED_KICAD_OBJECTS_DIR="$PROJECT_DIR/constant"

GENERATORS_DIR="$SOURCE_DIR/generators"
GENERATED_DIR="$PROJECT_DIR/generated"


# Delete generated dir
echo "Cleaning generated directory..."
rm -rf "$GENERATED_DIR"

# Copy kicad objects from hardcoded folders
if [ -d "$FIXED_KICAD_OBJECTS_DIR" ]; then
	echo "Copying constant footprints..."
	cp --recursive "$FIXED_KICAD_OBJECTS_DIR" "$GENERATED_DIR"
fi

# Generate kicad objects
echo "Generating footprints..."
uv run python "$YAML_GENERATOR_SCRIPT"		\
	--definitions-dir "$DEFINITIONS_DIR"	\
	--generators-dir "$GENERATORS_DIR"		\
	--output-dir "$GENERATED_DIR"			\
	--log-level "INFO"

echo "...Done!"
