"""
Code to load light curves in the background so they show up quickly when displayed.
"""
import asyncio
from collections import deque
from pathlib import Path
from typing import Union, List, NamedTuple, Deque

from ramjet.photometric_database.light_curve import LightCurve
from ramjet.photometric_database.tess_two_minute_cadence_light_curve import TessTwoMinuteCadenceLightCurve


class IndexLightCurvePair(NamedTuple):
    """A simple tuple linking an index and a light curve."""
    index: int
    light_curve: LightCurve


class Preloader:
    """
    A class to load light curves in the background so they show up quickly when displayed.
    """
    minimum_preloaded = 5
    maximum_preloaded = 10

    def __init__(self):
        self.current_index_light_curve_pair: Union[None, IndexLightCurvePair] = None
        self.next_index_light_curve_pairs_deque: Deque[IndexLightCurvePair] = deque(maxlen=self.maximum_preloaded)
        self.previous_index_light_curve_pairs_deque: Deque[IndexLightCurvePair] = deque(maxlen=self.maximum_preloaded)
        self.light_curve_path_list: List[Path] = []

    async def load_surrounding_light_curves(self):
        """
        Loads the next and previous light curves relative to the current light curve.
        """
        await self.load_next_light_curves()
        await self.load_previous_light_curves()

    async def load_light_curve_at_index_as_current(self, index):
        """
        Loads the light curve at the passed index as the current light curve.

        :param index: The index in the path list to load.
        """
        loop = asyncio.get_running_loop()
        current_light_curve = await loop.run_in_executor(None, self.load_light_curve_from_path,
                                                         self.light_curve_path_list[index])
        self.current_index_light_curve_pair = IndexLightCurvePair(index, current_light_curve)

    async def load_next_light_curves(self):
        """
        Preload the next light curves.
        """
        loop = asyncio.get_running_loop()
        if len(self.next_index_light_curve_pairs_deque) > 0:
            last_index = self.next_index_light_curve_pairs_deque[-1].index
        else:
            last_index = self.current_index_light_curve_pair.index
        while (len(self.next_index_light_curve_pairs_deque) < self.minimum_preloaded and
               last_index != len(self.light_curve_path_list) - 1):
            last_index += 1
            last_light_curve = await loop.run_in_executor(None, self.load_light_curve_from_path,
                                                          self.light_curve_path_list[last_index])
            last_index_light_curve_pair = IndexLightCurvePair(last_index, last_light_curve)
            self.next_index_light_curve_pairs_deque.append(last_index_light_curve_pair)

    async def load_previous_light_curves(self):
        """
        Preload the previous light curves.
        """
        loop = asyncio.get_running_loop()
        if len(self.previous_index_light_curve_pairs_deque) > 0:
            first_index = self.previous_index_light_curve_pairs_deque[0].index
        else:
            first_index = self.current_index_light_curve_pair.index
        while (len(self.previous_index_light_curve_pairs_deque) < self.minimum_preloaded and
               first_index != 0):
            first_index -= 1
            first_light_curve = await loop.run_in_executor(None, self.load_light_curve_from_path,
                                                           self.light_curve_path_list[first_index])
            first_index_light_curve_pair = IndexLightCurvePair(first_index, first_light_curve)
            self.previous_index_light_curve_pairs_deque.appendleft(first_index_light_curve_pair)

    @staticmethod
    def load_light_curve_from_path(path):
        """
        Loads a light curve from a path.

        :param path: The path of the light curve.
        :return: The light curve.
        """
        return TessTwoMinuteCadenceLightCurve.from_path(path)
