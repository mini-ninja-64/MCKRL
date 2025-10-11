# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABCMeta, abstractmethod
from KicadModTree import Footprint, Vector2D


class Stabiliser(metaclass=ABCMeta):
    def __init__(
        self,
        width_u: float,
        rotation: float,
        centre: Vector2D,
    ):
        self.width_u = width_u
        self.rotation = rotation
        self.centre = centre

    @abstractmethod
    def add_stabiliser_footprint(self, footprint: Footprint):
        pass
