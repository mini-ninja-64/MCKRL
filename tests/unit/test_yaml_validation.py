from pathlib import Path
import yaml
from mckrl.model import create_validation_model
from mckrl.generators.footprints.keyswitch import generate as keyswitch


def test_creating_model_for_generator_params():
    def generate(output_dir: str, a: int, b: bool, c: bool | None = None):
        pass

    model = create_validation_model(generate)
    empty = model.model_validate(
        yaml.safe_load((Path(__file__).parent / "empty.yaml").open())
    )


def test_validating_keyswitch_generate_yaml():
    model = create_validation_model(keyswitch.generate)
    validated = model.model_validate(
        yaml.safe_load(
            (
                Path(__file__).parent.parent.parent
                / "definitions/footprints/cherry_mx.pretty/standard.yaml"
            ).open()
        )
    )
    ...
