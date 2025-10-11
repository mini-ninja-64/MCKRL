# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
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


def isYamlFile(file: Path):
    return file.suffix.lower() in VALID_YAML_SUFFIXES


# TODO: The terms combination & combination set can be confusing and as such should be renamed
#       The "combinations" block in our yaml files, contain multiple "combination sets" which
#       are evaluated independently for all possible combinations and then combined
def getCombinationsForCombinationSet(
    combination_set: dict[str, list]
) -> list[dict[str, Any]]:
    if len(combination_set) == 0:
        return []
    allCombinations = [{}]
    for key, values in combination_set.items():
        combinations = []
        for value in values:

            def combinationCreator(combination):
                return {**combination, key: value}

            combinations.extend(map(combinationCreator, allCombinations))
        allCombinations = combinations
    return allCombinations


def getCombinations(combinations: list[dict[str, list]]) -> list[dict[str, Any]]:
    all_combinations = []
    for combination_set in combinations:
        all_combinations += getCombinationsForCombinationSet(combination_set)

    return all_combinations


def getPathInRelativeDirectory(relativeDir, path) -> Path:
    realDir = os.path.realpath(relativeDir)
    path = realDir + "/" + path
    return Path(path)


def loadPythonModuleFromFile(moduleName: str, path: Path):
    moduleSpec = importlib.util.spec_from_file_location(moduleName, path)
    module = importlib.util.module_from_spec(moduleSpec)
    moduleSpec.loader.exec_module(module)

    return module


def computeAllDefinitions(definitionDict: dict, baseDict: dict = {}) -> list[dict]:
    definitionDefault = definitionDict.get("defaults", {})
    definitionCombinations = getCombinations(definitionDict.get("combinations", []))
    definitionInputs = definitionDict["inputs"]

    # Create a dummy empty combination to keep our loop simple
    if len(definitionCombinations) == 0:
        definitionCombinations = [{}]

    definitions = []

    for definitionInput in definitionInputs:
        for definitionCombination in definitionCombinations:
            definitions.append(
                baseDict | definitionDefault | definitionCombination | definitionInput
            )

    return definitions


@click.command()
@click.option(
    "--definitions-dir", "-d", "definitionsDirectory", required=True, type=str
)
@click.option("--generators-dir", "-g", "generatorsDirectory", required=True, type=str)
@click.option("--output-dir", "-o", "outputDirectory", required=True, type=str)
@click.option(
    "--log-level",
    "-L",
    "logLevel",
    required=False,
    type=click.Choice(logging._nameToLevel.keys(), case_sensitive=False),
)
def generateKicadObjects(
    definitionsDirectory: str,
    generatorsDirectory: str,
    outputDirectory: str,
    logLevel: str,
):
    if logLevel is not None:
        logging.getLogger().setLevel(logLevel.upper())

    filesInDefinitionDir: list[Path] = list(Path(definitionsDirectory).rglob("*.*"))
    yamlPaths = filter(isYamlFile, filesInDefinitionDir)

    # TODO: make sure everything is a pathlib Path
    for yamlPath in yamlPaths:
        with open(yamlPath) as yamlFile:
            definitionDict = yaml.load(yamlFile, Loader=SafeLoader)
            validate(definitionDict, DEFINITION_SCHEMA)

            generatorFile = getPathInRelativeDirectory(
                generatorsDirectory, definitionDict["generator"]
            )

            # TODO: forward slashes assume *nix, we should consider Windows
            module_path = os.path.splitext(
                os.path.basename(generatorsDirectory)
                + "/"
                + os.path.relpath(generatorFile, generatorsDirectory)
            )[0]
            module_name = str(module_path).replace("/", ".")
            module = loadPythonModuleFromFile(module_name, generatorFile)

            yamlPathRelativeToDefinitions = yamlPath.relative_to(definitionsDirectory)
            outputDirectoryForYamlGeneratedResources = Path(
                os.path.realpath(outputDirectory)
                + "/"
                + str(yamlPathRelativeToDefinitions.parent)
            )
            outputDirectoryForYamlGeneratedResources.mkdir(parents=True, exist_ok=True)

            baseDict = {"output_dir": outputDirectoryForYamlGeneratedResources}
            definitions = computeAllDefinitions(definitionDict, baseDict)

            logging.info(
                "Found %i definitions in '%s'",
                len(definitions),
                yamlPathRelativeToDefinitions,
            )

            for definition in definitions:
                module.generate(**definition)


if __name__ == "__main__":
    generateKicadObjects()
