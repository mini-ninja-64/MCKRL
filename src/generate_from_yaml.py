# SPDX-License-Identifier: GPL-3.0-or-later

import importlib.util
import logging
import click
import yaml
import os
from jsonschema import validate

from pathlib import Path
from yaml.loader import SafeLoader
from typing import Any, Final

VALID_YAML_SUFFIXES: Final[list[str]] = [".yaml", ".yml"]

DEFINITION_SCHEMA: Final[dict] = {
    "type": "object",
    "required": ["generator", "inputs"],
    "properties": {
        "generator": {"type": "string"},
        "defaults": {"type": "object"},
        "combinations": {
            "type": "array",
            "items": {
                "type": "object",
                "patternProperties": {"^.*$": {"type": "array"}},
            },
        },
        "inputs": {
            "type": "array",
            "items": {
                "type": "object",
            },
        },
    },
    "additionalProperties": False,
}


def is_yaml_file(file: Path):
    return file.suffix.lower() in VALID_YAML_SUFFIXES


# TODO: The terms combination & combination set can be confusing and as such should be renamed
#       The "combinations" block in our yaml files, contain multiple "combination sets" which
#       are evaluated independently for all possible combinations and then combined
def get_combinations_for_combination_set(
    combination_set: dict[str, list],
) -> list[dict[str, Any]]:
    if len(combination_set) == 0:
        return []
    all_combinations = [{}]
    for key, values in combination_set.items():
        combinations = []
        for value in values:

            def combination_creator(combination):
                return {**combination, key: value}

            combinations.extend(map(combination_creator, all_combinations))
        all_combinations = combinations
    return all_combinations


def get_combinations(combinations: list[dict[str, list]]) -> list[dict[str, Any]]:
    all_combinations = []
    for combination_set in combinations:
        all_combinations += get_combinations_for_combination_set(combination_set)

    return all_combinations


def get_path_in_relative_directory(relative_dir, path) -> Path:
    real_dir = os.path.realpath(relative_dir)
    path = real_dir + "/" + path
    return Path(path)


def load_python_module_from_file(module_name: str, path: Path):
    module_spec = importlib.util.spec_from_file_location(module_name, path)
    if module_spec is None:
        raise RuntimeError(
            "ModuleSpec could not be generated for module '{moduleName}' at path '{path}'"
        )
    module = importlib.util.module_from_spec(module_spec)
    if module_spec.loader is None:
        raise RuntimeError(
            "Generated ModuleSpec has no loader for module '{moduleName}' at path '{path}'"
        )
    module_spec.loader.exec_module(module)

    return module


def compute_all_definitions(definition_dict: dict, base_dict: dict = {}) -> list[dict]:
    definition_default = definition_dict.get("defaults", {})
    definition_combinations = get_combinations(definition_dict.get("combinations", []))
    definition_inputs = definition_dict["inputs"]

    # Create a dummy empty combination to keep our loop simple
    if len(definition_combinations) == 0:
        definition_combinations = [{}]

    definitions = []

    for definition_input in definition_inputs:
        for definition_combination in definition_combinations:
            definitions.append(
                base_dict | definition_default | definition_combination | definition_input
            )

    return definitions


@click.command()
@click.option(
    "--definitions-dir", "-d", "definitions_directory", required=True, type=str
)
@click.option("--generators-dir", "-g", "generators_directory", required=True, type=str)
@click.option("--output-dir", "-o", "output_directory", required=True, type=str)
@click.option(
    "--log-level",
    "-L",
    "logLevel",
    required=False,
    type=click.Choice(logging._nameToLevel.keys(), case_sensitive=False),
)
def generate_kicad_objects(
    definitions_directory: str,
    generators_directory: str,
    output_directory: str,
    log_level: str,
):
    if log_level is not None:
        logging.getLogger().setLevel(log_level.upper())

    files_in_definition_dir: list[Path] = list(Path(definitions_directory).rglob("*.*"))
    yaml_paths = filter(is_yaml_file, files_in_definition_dir)

    # TODO: make sure everything is a pathlib Path
    for yaml_path in yaml_paths:
        with open(yaml_path) as yaml_file:
            definition_dict = yaml.load(yaml_file, Loader=SafeLoader)
            validate(definition_dict, DEFINITION_SCHEMA)

            generator_file = get_path_in_relative_directory(
                generators_directory, definition_dict["generator"]
            )

            # TODO: forward do not work on Windows
            module_path = os.path.splitext(
                os.path.basename(generators_directory)
                + "/"
                + os.path.relpath(generator_file, generators_directory)
            )[0]
            module_name = str(module_path).replace("/", ".")
            module = load_python_module_from_file(module_name, generator_file)

            yaml_path_relative_to_definitions = yaml_path.relative_to(definitions_directory)
            output_directory_for_yaml_generated_resources = Path(
                os.path.realpath(output_directory)
                + "/"
                + str(yaml_path_relative_to_definitions.parent)
            )
            output_directory_for_yaml_generated_resources.mkdir(parents=True, exist_ok=True)

            base_dict = {"output_dir": output_directory_for_yaml_generated_resources}
            definitions = compute_all_definitions(definition_dict, base_dict)

            logging.info(
                "Found %i definitions in '%s'",
                len(definitions),
                yaml_path_relative_to_definitions,
            )

            for definition in definitions:
                module.generate(**definition)


if __name__ == "__main__":
    generate_kicad_objects()
