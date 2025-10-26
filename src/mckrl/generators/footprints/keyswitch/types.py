import pydantic


class StabiliserParams(pydantic.BaseModel):
    type: str
    size: str
    rotation: float

    @pydantic.field_validator("rotation")
    @classmethod
    def normalize_rotation(cls, v: float):
        return v % 360
