import inspect
from pathlib import Path
from typing import Callable

import pydantic
from pydantic import ConfigDict


def create_validation_model(generate_func: Callable) -> type[pydantic.BaseModel]:
    params = inspect.getfullargspec(generate_func)

    annotations = {
        key: val for key, val in params.annotations.items() if key != "output_dir"
    }
    params_model = pydantic.create_model(
        "GenerateParams",
        **{key: (t | None, None) for key, t in annotations.items()},  # type: ignore
        __config__=ConfigDict(extra="forbid"),
    )
    combinations_model = pydantic.create_model(
        "GenerateCombinations",
        **{key: (list[t] | None, None) for key, t in annotations.items()},  # type: ignore
        __config__=ConfigDict(extra="forbid"),
    )

    return pydantic.create_model(
        "GenerateSpec",
        generator=Path,
        defaults=params_model,
        combinations=list[combinations_model],
        inputs=list[params_model],
    )
