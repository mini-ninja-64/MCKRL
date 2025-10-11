# SPDX-License-Identifier: Apache-2.0

from .stabiliser import Stabiliser
from .. import common
from KicadModTree import Footprint, Vector2D, PolygonLine

STAB_BIG_HOLE_DIAMETER = 4
STAB_SMALL_HOLE_DIAMETER = 3.05

CHERRY_STABILISER_WIDTH: dict[int | float, float] = {
    2: 23.876,  # 0.94in (1.2533...u) TODO: check this one kicad seems to think its 23.8mm (https://cdn.sparkfun.com/datasheets/Components/Switches/MX%20Series.pdf vs https://datasheet.octopart.com/MX1A-C1NW-Cherry-datasheet-15918975.pdf)
    3: 38.1,  # 1.5in (2u)
    5: 76.2,  # 3in (4u), TODO: technically 5u spacebar not exist, only used in this example for sp 6u maybe enum style thing would suit stabs better
    6: 95.25,  # 3.75in (5u)
    6.25: 100,  # 3.93701in (5.2493466...u)
    7: 114.3,  # 4.5in (6u)
    8: 133.35,  # 5.25in (7u)
}

STAB_VERTICAL_OFFSET = 1.25  # vertical centre is offset from switch position
STAB_HEIGHT = 20
STAB_WIDTH = 7
STAB_WIRE_BUFFER = 4  # add room for the stabiliser wire


class CherryStabiliser(Stabiliser):
    def __init__(
        self,
        width_u: float,
        rotation: float,
        centre: Vector2D = Vector2D(0, 0),
    ):
        super().__init__(width_u, rotation, centre)

        width = CHERRY_STABILISER_WIDTH.get(self.width_u)

        if width is None:
            raise Exception(f"Unsupported stabiliser size: {self.width_u}")

        self.__stabiliser_centre_distance = width / 2

    def add_stabiliser_footprint(self, footprint: Footprint):
        common.add_npth_hole(
            kicad_mod=footprint,
            centre=Vector2D(
                self.centre.x - self.__stabiliser_centre_distance,
                self.centre.y - 7,
            ),
            diameter=STAB_SMALL_HOLE_DIAMETER,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        common.add_npth_hole(
            kicad_mod=footprint,
            centre=Vector2D(
                self.centre.x - self.__stabiliser_centre_distance,
                self.centre.y + 8.24,
            ),
            diameter=STAB_BIG_HOLE_DIAMETER,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        common.add_npth_hole(
            kicad_mod=footprint,
            centre=Vector2D(
                self.centre.x + self.__stabiliser_centre_distance,
                self.centre.y - 7,
            ),
            diameter=STAB_SMALL_HOLE_DIAMETER,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        common.add_npth_hole(
            kicad_mod=footprint,
            centre=Vector2D(
                self.centre.x + self.__stabiliser_centre_distance,
                self.centre.y + 8.24,
            ),
            diameter=STAB_BIG_HOLE_DIAMETER,
            rotation=self.rotation,
            rotation_origin=self.centre,
        )

        self.__add_stabiliser_courtyard(footprint, self.__stabiliser_centre_distance)

    def __add_stabiliser_courtyard(self, footprint: Footprint, half_width: float):
        centre_y = self.centre.y + STAB_VERTICAL_OFFSET
        line = PolygonLine(
            shape=[
                [
                    self.centre.x - half_width - (STAB_WIDTH / 2),
                    centre_y - (STAB_HEIGHT / 2),
                ],
                [
                    self.centre.x - half_width + (STAB_WIDTH / 2),
                    centre_y - (STAB_HEIGHT / 2),
                ],
                [
                    self.centre.x - half_width + (STAB_WIDTH / 2),
                    (centre_y + (STAB_HEIGHT / 2)) - STAB_WIRE_BUFFER,
                ],
                [
                    self.centre.x + half_width - (STAB_WIDTH / 2),
                    (centre_y + (STAB_HEIGHT / 2)) - STAB_WIRE_BUFFER,
                ],
                [
                    self.centre.x + half_width - (STAB_WIDTH / 2),
                    centre_y - (STAB_HEIGHT / 2),
                ],
                [
                    self.centre.x + half_width + (STAB_WIDTH / 2),
                    centre_y - (STAB_HEIGHT / 2),
                ],
                [
                    self.centre.x + half_width + (STAB_WIDTH / 2),
                    centre_y + (STAB_HEIGHT / 2),
                ],
                [
                    self.centre.x - half_width - (STAB_WIDTH / 2),
                    centre_y + (STAB_HEIGHT / 2),
                ],
                [
                    self.centre.x - half_width - (STAB_WIDTH / 2),
                    centre_y - (STAB_HEIGHT / 2),
                ],
            ],
            layer="F.CrtYd",
        )
        footprint.append(line.rotate(origin=self.centre, angle=self.rotation))
