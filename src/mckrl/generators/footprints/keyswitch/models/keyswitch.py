# SPDX-License-Identifier: Apache-2.0

from abc import ABCMeta, abstractmethod
from KicadModTree import Footprint, Vector2D


class Keyswitch(metaclass=ABCMeta):
    def __init__(self, rotation: float, centre: Vector2D):
        self.rotation = rotation
        self.centre = centre

    @abstractmethod
    def add_switch_footprint(self, footprint: Footprint):
        pass
