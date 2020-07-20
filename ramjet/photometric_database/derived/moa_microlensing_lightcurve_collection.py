"""
Code for a lightcurve collection of the MOA data.
"""
from pathlib import Path
from typing import Iterable
import numpy as np
import pandas as pd

from ramjet.photometric_database.lightcurve_collection import LightcurveCollection
from ramjet.photometric_database.microlensing_signal_generator import MagnificationSignal
import random


class MOAPositiveMicrolensingLightcurveCollection(LightcurveCollection):
    """
    A lightcurve collection of the MOA data with previously detected microlensing events.
    """

    def __init__(self, dataset_splits=None, split_pieces=5):
        super().__init__()
        self.label = 1
        self.split_pieces = split_pieces
        if dataset_splits is None:
            dataset_splits = [1, 2, 3, 4]
        self.dataset_splits = dataset_splits

    def get_paths(self) -> Iterable[Path]:
        """
        Gets the paths for the lightcurves in the positive collection.

        :return: An iterable of the lightcurve paths.
        """
        paths = Path('/local/data/fugu3/sishitan/ramjet/data/moa_microlensing/positive').glob('*.feather')
        path_list = list(paths)
        random.seed(42)
        random.shuffle(path_list)
        number_of_samples = len(path_list)
        number_of_samples_per_block = number_of_samples // self.split_pieces
        dataset_paths = []
        for block in self.dataset_splits:
            dataset_paths += path_list[block*number_of_samples_per_block:(block+1)*number_of_samples_per_block]
        return dataset_paths

    def load_times_and_fluxes_from_path(self, path: Path) -> (np.ndarray, np.ndarray):
        """
        Loads the times and fluxes from a given lightcurve path.

        :param path: The path to the lightcurve file.
        :return: The times and the fluxes of the lightcurve.
        """
        lightcurve_dataframe = pd.read_feather(path)
        times = lightcurve_dataframe['HJD'].values
        fluxes = lightcurve_dataframe['flux'].values
        return times, fluxes


class MOANegativeMicrolensingLightcurveCollection(LightcurveCollection):
    """
    A lightcurve collection of the MOA data with no microlensing event.
    """

    def __init__(self, dataset_splits=None, split_pieces=5):
        super().__init__()
        self.label = 0
        self.split_pieces = split_pieces
        if dataset_splits is None:
            dataset_splits = [1, 2, 3, 4]
        self.dataset_splits = dataset_splits

    def get_paths(self):
        """
        Gets the paths for the lightcurves in the negative collection.

        :return: An iterable of the lightcurve paths.
        """
        paths = Path('/local/data/fugu3/sishitan/ramjet/data/moa_microlensing/negative').glob('*.feather')
        path_list = list(paths)
        random.seed(42)
        random.shuffle(path_list)
        number_of_samples = len(path_list)
        number_of_samples_per_block = number_of_samples // self.split_pieces
        dataset_paths = []
        for block in self.dataset_splits:
            dataset_paths += path_list[block*number_of_samples_per_block:(block+1)*number_of_samples_per_block]
        return dataset_paths

    def load_times_and_fluxes_from_path(self, path: Path) -> (np.ndarray, np.ndarray):
        """
        Loads the times and fluxes from a given lightcurve path.

        :param path: The path to the lightcurve file.
        :return: The times and the fluxes of the lightcurve.
        """
        lightcurve_dataframe = pd.read_feather(path)
        times = lightcurve_dataframe['HJD'].values
        fluxes = lightcurve_dataframe['flux'].values
        return times, fluxes


class MicrolensingSyntheticPSPLSignalCollection(LightcurveCollection):
    def __init__(self):
        super().__init__()
        self.label = 1

    def get_paths(self):
        """
        Gets the paths for the PSPL microlensing signals.

        :return: An iterable of the lightcurve paths.
        """
        paths = Path('/local/data/fugu3/sishitan/muLAn_project/PSPL').glob('*.feather')
        return paths

    def load_times_and_magnifications_from_path(self, path: Path) -> (np.ndarray, np.ndarray):
        """
        Loads the times and magnifications from a given path as an injectable signal.

        :param path: The path to the lightcurve/signal file.
        :return: The times and the magnifications of the lightcurve/signal.
        """
        signal_dataframe = pd.read_feather(path)
        times = signal_dataframe['Time'].values
        magnifications = signal_dataframe['Magnification'].values
        return times, magnifications


class MicrolensingSyntheticGeneratedDuringRunningSignalCollection(LightcurveCollection):
    def __init__(self):
        super().__init__()
        self.label = 1

    def get_paths(self) -> Iterable[Path]:
        """
        No need to get paths because this function will generate the signals on the fly.

        :return: empty generator.
        """

        return [Path('')]

    def load_times_and_magnifications_from_path(self, path: Path) -> (np.ndarray, np.ndarray):
        """
        Loads the times and magnifications from a random generated signal.

        :param path: empty path
        :return: The times and the magnifications of the signal.
        """
        random_signal = MagnificationSignal.generate_randomly_based_on_moa_observations()
        return random_signal.timeseries, random_signal.magnification
