# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

import pydantic
from . import models, conversion, common
from KicadModTree import Footprint, FootprintType, Vector2D, KicadFileHandler


class StabiliserParams(pydantic.BaseModel):
    type: str
    size: str
    rotation: float

    @pydantic.field_validator("rotation")
    @classmethod
    def normalize_rotation(cls, v: float):
        return v % 360


def generate(
    output_dir: str,
    prefix: str,
    switch_type: str,
    width: str,
    spacing: str,
    rotation: float = 0,
    led: bool = False,
    diode: bool = False,
    switch_horizontal_offset: str = "0u",
    stabiliser_type: str | None = None,
    stabiliser_size: str | None = None,
    stabiliser_rotation: float = 0,
):
    # Validate both required stabiliser args are provided or neither
    if [stabiliser_type, stabiliser_size].count(None) == 1:
        raise ValueError(
            "Please ensure both 'stabiliser_type' & 'stabiliser_size' are provided"
        )
    elif stabiliser_type is not None and stabiliser_size is not None:
        stabiliser_params = StabiliserParams(
            type=stabiliser_type, size=stabiliser_size, rotation=stabiliser_rotation
        )
    else:
        stabiliser_params = None

    if prefix is None:
        raise Exception("No prefix provided.")

    switch_spacing_mm = conversion.string_to_millimetre_float(spacing)

    def normalise_measurement(s):
        return conversion.string_to_millimetre_float(s, {"u": switch_spacing_mm})

    width_u = conversion.get_switch_width_in_units(width)
    width_mm = normalise_measurement(width)
    switch_centre = Vector2D(normalise_measurement(switch_horizontal_offset), 0)
    rotation %= 360

    footprint_name = common.create_footprint_name(
        prefix=prefix,
        led=led,
        diode=diode,
        switch_spacing_mm=switch_spacing_mm,
        width_u=width_u,
        switch_rotation=rotation,
        stabiliser_params=stabiliser_params,
    )

    footprint_description = common.create_footprint_description(
        prefix=prefix,
        led=led,
        diode=diode,
        width_u=width_u,
        stabiliser_params=stabiliser_params,
    )

    keyswitch_footprint = Footprint(
        name=footprint_name, footprint_type=FootprintType.THT
    )
    keyswitch_footprint.setDescription(footprint_description)
    keyswitch_footprint.tags = prefix

    if switch_type is not None:
        if switch_type == "cherry":
            if led & diode:
                raise Exception("Switch footprints cannot have both LEDs and diodes.")

            switch = models.CherryKeyswitch(
                rotation=rotation,
                centre=switch_centre,
                led=led,
                diode=diode,
            )

        elif switch_type == "alps":
            switch = models.AlpsKeyswitch(
                rotation=rotation,
                centre=switch_centre,
                led=led,
            )

        else:
            raise Exception(f"{switch_type} is not supported.")

        switch.add_switch_footprint(footprint=keyswitch_footprint)

    if stabiliser_params is not None:
        stabiliser = None
        if stabiliser_params.type == "cherry":
            stabiliser = models.CherryStabiliser(
                conversion.get_switch_width_in_units(stabiliser_params.size),
                stabiliser_params.rotation,
            )
        else:
            raise Exception(f"{stabiliser_params.type} is not supported.")

        stabiliser.add_stabiliser_footprint(footprint=keyswitch_footprint)

    spacing_box_rotation = (
        stabiliser_params.rotation if stabiliser_params is not None else 0
    )
    common.add_spacing_rectangle(
        keyswitch_footprint,
        width_mm,
        switch_spacing_mm,
        spacing_box_rotation,
    )
    print(f"{footprint_name} - {spacing_box_rotation}")
    common.add_footprint_labels(keyswitch_footprint, switch_spacing_mm)

    file_handler = KicadFileHandler(keyswitch_footprint)
    file_path = f"{output_dir}/{footprint_name}.kicad_mod"
    file_handler.writeFile(Path(file_path))
