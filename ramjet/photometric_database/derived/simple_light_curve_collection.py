import numpy as np
from pathlib import Path
from typing import Iterable

from ramjet.photometric_database.lightcurve_collection import LightcurveCollection


class SimpleLightCurveCollection(LightcurveCollection):
    """
    A simple positive and negative directory based light curve collection.
    """
    def __init__(self, collection_directory: Path = Path('data/simple_test_dataset')):
        super().__init__()
        self.collection_directory = collection_directory

    def get_paths(self) -> Iterable[Path]:
        """
        Gets the paths for the lightcurves in the collection.

        :return: An iterable of the lightcurve paths.
        """
        return self.collection_directory.glob('**/*.npz')

    def load_times_and_fluxes_from_path(self, path: Path) -> (np.ndarray, np.ndarray):
        """
        Loads the times and fluxes from a given lightcurve path.

        :param path: The path to the lightcurve file.
        :return: The times and the fluxes of the lightcurve.
        """
        contents = np.load(str(path))
        times = contents['times']
        fluxes = contents['fluxes']
        return times, fluxes
