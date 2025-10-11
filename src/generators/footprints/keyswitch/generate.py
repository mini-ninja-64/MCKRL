# SPDX-License-Identifier: GPL-3.0-or-later

from . import models, conversion, common
from KicadModTree import Footprint, FootprintType, Vector2D, KicadFileHandler


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
    stabiliser_type: str = None,
    stabiliser_size: float = None,
    stabiliser_rotation: float = 0,
):
    if prefix is None:
        raise Exception("No prefix provided.")

    switch = stabiliser = None

    switch_spacing_mm = conversion.string_to_millimetre_float(spacing)
    normalise_measurement = lambda s: conversion.string_to_millimetre_float(
        s, {"u": switch_spacing_mm}
    )
    width_u = conversion.get_switch_width_in_units(width)
    width_mm = normalise_measurement(width)
    switch_centre = Vector2D(normalise_measurement(switch_horizontal_offset), 0)
    rotation %= 360
    stabiliser_rotation %= 360

    footprint_name = common.create_footprint_name(
        prefix=prefix,
        led=led,
        diode=diode,
        switch_spacing_mm=switch_spacing_mm,
        width_u=width_u,
        switch_rotation=rotation,
        stabiliser_rotation=stabiliser_rotation,
    )

    footprint_description = common.create_footprint_description(
        prefix=prefix,
        led=led,
        diode=diode,
        switch=switch,
        width_u=width_u,
        stabiliser_size=stabiliser_size,
        switch_rotation=rotation,
        stabiliser_rotation=stabiliser_rotation,
    )

    keyswitch_footprint = Footprint(name=footprint_name, footprint_type=FootprintType.THT)
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

    if stabiliser_type is not None:
        stabiliser_size = conversion.get_switch_width_in_units(stabiliser_size)

        if stabiliser_type == "cherry":
            stabiliser = models.CherryStabiliser(stabiliser_size, stabiliser_rotation)

        else:
            raise Exception(f"{stabiliser_type} is not supported.")

        stabiliser.add_stabiliser_footprint(footprint=keyswitch_footprint)

    common.add_spacing_rectangle(
        keyswitch_footprint,
        width_mm,
        switch_spacing_mm,
        stabiliser_rotation,
    )
    common.add_footprint_labels(keyswitch_footprint, switch_spacing_mm)

    file_handler = KicadFileHandler(keyswitch_footprint)
    file_path = f"{output_dir}/{footprint_name}.kicad_mod"
    file_handler.writeFile(file_path)
