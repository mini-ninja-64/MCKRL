# SPDX-License-Identifier: Apache-2.0

import importlib.util
import subprocess
from loguru import logger
from rich.logging import RichHandler
import rich.progress
import typer
import yaml
import os
from jsonschema import validate

from pathlib import Path
from yaml.loader import SafeLoader
from typing import Annotated, Any, Final

from mckrl.model import create_validation_model

logger.configure(handlers=[{"sink": RichHandler(), "format": "{message}"}])

VALID_YAML_SUFFIXES: Final[list[str]] = [".yaml", ".yml"]


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
                base_dict
                | definition_default
                | definition_combination
                | definition_input
            )

    return definitions


def copy_constants(constants_directory: Path, output_directory: Path):
    logger.info(f"Clearing output dir: {output_directory}")
    subprocess.check_call(["rm", "-rf", str(output_directory)])
    logger.info(
        f"Copying constant footprints {constants_directory} -> {output_directory}"
    )
    subprocess.check_call(["cp", "-r", str(constants_directory), str(output_directory)])


cli = typer.Typer(add_completion=False)


@cli.command()
def main(
    definitions_directory: Annotated[Path, typer.Option("--definitions", "-d")] = Path(
        "definitions"
    ),
    generators_directory: Annotated[
        Path, typer.Option(..., "--generators", "-g")
    ] = Path("src/mckrl/generators"),
    output_directory: Annotated[Path, typer.Option(..., "--output", "-o")] = Path(
        "generated"
    ),
    constants_directory: Annotated[Path, typer.Option(..., "--constants", "-c")] = Path(
        "constant"
    ),
):
    copy_constants(constants_directory, output_directory)
    generate_kicad_objects(
        definitions_directory, generators_directory, output_directory
    )


def generate_kicad_objects(
    definitions_directory, generators_directory, output_directory
):
    files_in_definition_dir: list[Path] = list(definitions_directory.rglob("*.*"))
    yaml_paths = list(filter(is_yaml_file, files_in_definition_dir))

    for yaml_path in rich.progress.track(
        yaml_paths, description="Processing definition files"
    ):
        with open(yaml_path) as yaml_file:
            definition_dict = yaml.load(yaml_file, Loader=SafeLoader)

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

            model = create_validation_model(module.generate)
            validate(definition_dict, model.model_json_schema())

            yaml_path_relative_to_definitions = yaml_path.relative_to(
                definitions_directory
            )
            output_directory_for_yaml_generated_resources = (
                output_directory.resolve() / yaml_path_relative_to_definitions.parent
            )
            output_directory_for_yaml_generated_resources.mkdir(
                parents=True, exist_ok=True
            )

            base_dict = {"output_dir": output_directory_for_yaml_generated_resources}
            definitions = compute_all_definitions(definition_dict, base_dict)

            logger.info(
                f"Found {len(definitions)} definitions in {yaml_path_relative_to_definitions}",
            )

            for definition in rich.progress.track(definitions, transient=True):
                module.generate(**definition)
