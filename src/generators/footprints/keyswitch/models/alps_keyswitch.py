# SPDX-License-Identifier: GPL-3.0-or-later

from .keyswitch import Keyswitch
from .. import common
from KicadModTree import Footprint, Vector2D, Pad, RectLine

THT_PAD_DIAMETER = 2.54
THT_PAD_DRILL = 1.5
LED_SPACING = 1.27
LED_HOLE_DIAMETER = 1.905
LED_HOLE_DRILL = 1
COURTYARD_WIDTH = 15.5
COURTYARD_HEIGHT = 12.8


class AlpsKeyswitch(Keyswitch):
    def __init__(
        self,
        rotation: float,
        centre: Vector2D,
        led: bool,
    ):
        super().__init__(rotation=rotation, centre=centre)
        self.led = led

    def add_switch_footprint(
        self,
        footprint: Footprint,
    ):
        # Create Solder pads for switch
        common.add_tht_hole(
            kicad_mod=footprint,
            pad_pin=1,
            centre=[2.5 + self.centre.x, -4.5],
            diameter=THT_PAD_DIAMETER,
            inner_diameter=THT_PAD_DRILL,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        common.add_tht_hole(
            kicad_mod=footprint,
            pad_pin=2,
            centre=[-2.5 + self.centre.x, -4],
            diameter=THT_PAD_DIAMETER,
            inner_diameter=THT_PAD_DRILL,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        self.__add_switch_courtyard(footprint)

        if self.led:
            self.__add_led_holes(footprint)

    def __add_switch_courtyard(self, footprint: Footprint):
        footprint.append(
            RectLine(
                start=[-COURTYARD_WIDTH / 2, -COURTYARD_HEIGHT / 2],
                end=[COURTYARD_WIDTH / 2, COURTYARD_HEIGHT / 2],
                layer="F.CrtYd",
                angle=self.rotation,
            )
        )

    def __add_led_holes(self, footprint: Footprint):
        common.add_tht_hole(
            kicad_mod=footprint,
            pad_pin=3,
            centre=[-LED_SPACING + self.centre.x, 4.6],
            diameter=LED_HOLE_DIAMETER,
            inner_diameter=LED_HOLE_DRILL,
            rotation=self.rotation,
            rotation_origin=self.centre,
            pad_shape=Pad.SHAPE_ROUNDRECT,
        )

        common.add_tht_hole(
            kicad_mod=footprint,
            pad_pin=4,
            centre=[LED_SPACING + self.centre.x, 4.6],
            diameter=LED_HOLE_DIAMETER,
            inner_diameter=LED_HOLE_DRILL,
            rotation=self.rotation,
            rotation_origin=self.centre,
            pad_shape=Pad.SHAPE_CIRCLE,
        )
