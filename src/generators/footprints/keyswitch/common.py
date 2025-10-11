# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Literal
from KicadModTree import (
    Footprint,
    Property,
    RoundRadiusHandler,
    Vector2D,
    Pad,
    RectLine,
)

from generators.footprints.keyswitch.generate import StabiliserParams


def create_footprint_name(
    prefix: str,
    led: bool,
    diode: bool,
    switch_spacing_mm: float,
    width_u: float,
    switch_rotation: float,
    stabiliser_params: StabiliserParams | None,
) -> str:
    switch_accessory = ""

    if led:
        switch_accessory += "LED_"

    if diode:
        switch_accessory += "diode_"

    name = f"{prefix}_{switch_accessory}{switch_spacing_mm}mm_{width_u}u"

    if switch_rotation != 0:
        name += get_rotation_description(
            angle=switch_rotation,
            suffix="switch",
            string_type="name",
        )

    if stabiliser_params is not None and stabiliser_params.rotation != 0:
        name += get_rotation_description(
            angle=stabiliser_params.rotation,
            suffix="stab",
            string_type="name",
        )

    return name


def create_footprint_description(
    prefix: str,
    led: bool,
    diode: bool,
    width_u: float,
    stabiliser_params: StabiliserParams | None,
) -> str:
    manufacturer = prefix.split("_")[0].title()
    product_code = prefix.split("_")[1]
    indefinite_article = "A"

    if is_vowel(manufacturer[0]):
        indefinite_article = "An"

    description = (
        f"{indefinite_article} {manufacturer} {product_code} footprint, {width_u}u wide"
    )

    extra_info = []

    if led:
        extra_info.append("an in-switch LED")
    if diode:
        extra_info.append("an in-switch diode")

    if stabiliser_params is not None:
        if stabiliser_params.rotation == 0:
            extra_info.append("a stabiliser")
        else:
            rotation_description = get_rotation_description(
                angle=stabiliser_params.rotation,
                suffix=None,
                string_type="description",
            )
            extra_info.append(rotation_description)

    if len(extra_info) > 1:
        description += " with " + ", ".join(extra_info[:-1]) + " and " + extra_info[-1]
    elif len(extra_info) == 1:
        description += " with " + extra_info[0]

    description += "."

    return description


def add_footprint_labels(footprint: Footprint, spacing: float):
    footprint.append(
        Property(
            name=Property.VALUE,
            text=footprint.name,
            at=[0, -(spacing / 2) * 0.9],
            layer="F.Fab",
        )
    )
    footprint.append(
        Property(
            name=Property.REFERENCE,
            text="REF**",
            at=[0, (spacing / 2) * 0.9],
            layer="F.Fab",
        )
    )


def get_rotation_description(
    angle: float,
    suffix: str | None,
    string_type: Literal["name", "description"],
) -> str:
    description_words = []
    if angle % 90 == 0:
        if angle == 90 or angle == 270:
            description_words.append("vertical")
        if angle == 180 or angle == 270:
            description_words.append("flipped")
    else:
        description_words = "{0}DEG".format(angle)

    if len(description_words) == 0:
        return ""

    if string_type == "name":
        return "_{0}-{1}".format("-".join(description_words), suffix)

    if string_type == "description":
        stabiliser_description = " ".join(word.lower() for word in description_words)
        return " ".join(["a", stabiliser_description, "stabiliser"])


def add_npth_hole(
    kicad_mod: Footprint,
    centre: Vector2D,
    rotation: float,
    diameter: float,
    rotation_origin: Vector2D = Vector2D(0, 0),
):
    kicad_mod.append(
        Pad(
            type=Pad.TYPE_NPTH,
            shape=Pad.SHAPE_CIRCLE,
            at=centre,
            size=Vector2D(diameter, diameter),
            drill=diameter,
            layers=Pad.LAYERS_NPTH,
        ).rotate(angle=rotation, origin=rotation_origin)
    )


# 'pad_pin' can be type hint of str | int, however this is not supported until 3.10
def add_tht_hole(
    kicad_mod: Footprint,
    centre: Vector2D,
    rotation: float,
    diameter: float,
    inner_diameter: float,
    pad_pin: int,
    pad_shape=Pad.SHAPE_CIRCLE,
    rotation_origin: Vector2D = Vector2D(0, 0),
):
    kicad_mod.append(
        Pad(
            number=pad_pin,
            type=Pad.TYPE_THT,
            shape=pad_shape,
            at=centre,
            size=Vector2D(diameter, diameter),
            drill=inner_diameter,
            layers=Pad.LAYERS_THT,
            round_radius_handler=RoundRadiusHandler(0.25),
        ).rotate(angle=rotation, origin=rotation_origin)
    )


def add_spacing_rectangle(
    footprint: Footprint, width: float, spacing: float, rotation: float
):
    footprint.append(
        RectLine(
            start=[-width / 2, -spacing / 2],
            end=[width / 2, spacing / 2],
            layer="Dwgs.User",
            angle=rotation,
        )
    )


def is_vowel(char: str):
    return char.lower() in ["a", "e", "i", "o", "u"]
