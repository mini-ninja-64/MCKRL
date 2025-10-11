# SPDX-License-Identifier: GPL-3.0-or-later

from .keyswitch import Keyswitch
from .. import common
from KicadModTree import Footprint, Vector2D, Pad

THT_PAD_DIAMETER = 2.54
THT_PAD_DRILL = 1.55
SWITCH_HOLE_DIAMETER = 4.1
MOUNT_PIN_DIAMETER = 1.7525
PIN_GRID = 1.27
SWITCH_ACCESSORY_HOLE_DIAMETER = 1.905
SWITCH_ACCESSORY_HOLE_DRILL = 1


class CherryKeyswitch(Keyswitch):
    def __init__(
        self,
        rotation: float,
        centre: Vector2D,
        led: bool,
        diode: bool,
    ):
        super().__init__(rotation=rotation, centre=centre)
        self.led = led
        self.diode = diode

    def add_switch_footprint(
        self,
        footprint: Footprint,
    ):
        # Create Solder pads for switch
        common.add_tht_hole(
            kicad_mod=footprint,
            pad_pin=1,
            centre=[-3.81 + self.centre.x, -2.54],
            diameter=THT_PAD_DIAMETER,
            inner_diameter=THT_PAD_DRILL,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        common.add_tht_hole(
            kicad_mod=footprint,
            pad_pin=2,
            centre=[2.54 + self.centre.x, -5.08],
            diameter=THT_PAD_DIAMETER,
            inner_diameter=THT_PAD_DRILL,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        # Create NPTHs of switch
        common.add_npth_hole(
            kicad_mod=footprint,
            centre=self.centre,
            diameter=SWITCH_HOLE_DIAMETER,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        common.add_npth_hole(
            kicad_mod=footprint,
            centre=[-5.08 + self.centre.x, self.centre.y],
            diameter=MOUNT_PIN_DIAMETER,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        common.add_npth_hole(
            kicad_mod=footprint,
            centre=[5.08 + self.centre.x, self.centre.y],
            diameter=MOUNT_PIN_DIAMETER,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        self.__add_switch_accessory_holes(footprint)

    def __add_switch_accessory_holes(self, footprint: Footprint):
        position_mapping = {
            0: -PIN_GRID * 3,
            1: -PIN_GRID,
            2: PIN_GRID,
            3: PIN_GRID * 3,
        }

        positions = []

        if self.diode:
            positions = [0, 3]

        if self.led:
            positions = [1, 2]

        for position in positions:
            common.add_tht_hole(
                kicad_mod=footprint,
                pad_pin=3 if position == 0 or position == 1 else 4,
                centre=[position_mapping[position] + self.centre.x, 5.08],
                diameter=SWITCH_ACCESSORY_HOLE_DIAMETER,
                inner_diameter=SWITCH_ACCESSORY_HOLE_DRILL,
                rotation=self.rotation,
                rotation_origin=self.centre,
                pad_shape=Pad.SHAPE_ROUNDRECT if position == 1 else Pad.SHAPE_CIRCLE,
            )
