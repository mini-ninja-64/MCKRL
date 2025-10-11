# SPDX-License-Identifier: Apache-2.0


def get_switch_width_in_units(string: str) -> float:
    if not string.endswith("u"):
        raise ValueError("Keyswitch footprint sizes should end with a 'u'")
    return float(string[:-1])


def string_to_millimetre_float(
    measurement_string: str, alternate_unit_lookup: dict[str, float] = {}
) -> float:
    unit_lookup = {
        "mm": 1,
        "cm": 10,
        "in": 25.4,
        "mils": 0.0254,
        **alternate_unit_lookup,
    }

    for unit_string, unit_multiplier in unit_lookup.items():
        if measurement_string.endswith(unit_string):
            number_string = measurement_string[: -len(unit_string)]
            return float(number_string) * unit_multiplier

    raise ValueError(f"Provided measurement unit not supported: {measurement_string}")
