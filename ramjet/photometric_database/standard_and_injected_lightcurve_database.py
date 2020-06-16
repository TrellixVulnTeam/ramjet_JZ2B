"""
An abstract class allowing for any number and combination of standard and injectable/injectee lightcurve collections.
"""
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import List, Union, Callable, Tuple

from ramjet.photometric_database.lightcurve_collection import LightcurveCollection
from ramjet.photometric_database.lightcurve_database import LightcurveDatabase
from ramjet.py_mapper import map_py_function_to_dataset


class StandardAndInjectedLightcurveDatabase(LightcurveDatabase):
    """
    An abstract class allowing for any number and combination of standard and injectable/injectee lightcurve collections
    to be used for training.
    """

    def __init__(self):
        super().__init__()
        self.training_standard_lightcurve_collections: List[LightcurveCollection] = []
        self.training_injectee_lightcurve_collection: Union[LightcurveCollection, None] = None
        self.training_injectable_lightcurve_collections: List[LightcurveCollection] = []
        self.validation_standard_lightcurve_collections: List[LightcurveCollection] = []
        self.validation_injectee_lightcurve_collection: Union[LightcurveCollection, None] = None
        self.validation_injectable_lightcurve_collections: List[LightcurveCollection] = []
        self.shuffle_buffer_size = 10000
        self.time_steps_per_example = 20000

    def generate_datasets(self) -> (tf.data.Dataset, tf.data.Dataset):
        training_standard_paths_datasets = self.generate_paths_datasets_from_lightcurve_collection_list(
            self.training_standard_lightcurve_collections)
        training_injectee_path_dataset = self.generate_paths_dataset_from_lightcurve_collection(
            self.training_injectee_lightcurve_collection)
        training_injectable_paths_datasets = self.generate_paths_datasets_from_lightcurve_collection_list(
            self.training_injectable_lightcurve_collections)
        validation_standard_paths_datasets = self.generate_paths_datasets_from_lightcurve_collection_list(
            self.validation_standard_lightcurve_collections)
        validation_injectee_path_dataset = self.generate_paths_dataset_from_lightcurve_collection(
            self.validation_injectee_lightcurve_collection)
        validation_injectable_paths_datasets = self.generate_paths_datasets_from_lightcurve_collection_list(
            self.validation_injectable_lightcurve_collections)
        training_lightcurve_and_label_datasets = []
        for paths_dataset, lightcurve_collection in zip(training_standard_paths_datasets,
                                                        self.training_standard_lightcurve_collections):
            lightcurve_and_label_dataset = self.generate_standard_lightcurve_and_label_dataset(
                paths_dataset, lightcurve_collection.label
            )
            training_lightcurve_and_label_datasets.append(lightcurve_and_label_dataset)
        for paths_dataset, injectable_lightcurve_collection in zip(training_injectable_paths_datasets,
                                                                   self.training_injectable_lightcurve_collections):
            lightcurve_and_label_dataset = self.generate_injected_lightcurve_and_label_dataset(
                training_injectee_path_dataset, paths_dataset, injectable_lightcurve_collection.label
            )
            training_lightcurve_and_label_datasets.append(lightcurve_and_label_dataset)
        training_dataset = tf.data.Dataset.zip(training_lightcurve_and_label_datasets)
        validation_lightcurve_and_label_datasets = []
        for paths_dataset, lightcurve_collection in zip(validation_standard_paths_datasets,
                                                        self.validation_standard_lightcurve_collections):
            lightcurve_and_label_dataset = self.generate_standard_lightcurve_and_label_dataset(
                paths_dataset, lightcurve_collection.label
            )
            validation_lightcurve_and_label_datasets.append(lightcurve_and_label_dataset)
        for paths_dataset, injectable_lightcurve_collection in zip(validation_injectable_paths_datasets,
                                                                   self.validation_injectable_lightcurve_collections):
            lightcurve_and_label_dataset = self.generate_injected_lightcurve_and_label_dataset(
                validation_injectee_path_dataset, paths_dataset, injectable_lightcurve_collection.label
            )
            validation_lightcurve_and_label_datasets.append(lightcurve_and_label_dataset)
        validation_dataset = tf.data.Dataset.zip(validation_lightcurve_and_label_datasets)
        return training_dataset, validation_dataset

    def generate_paths_dataset_from_lightcurve_collection(self, lightcurve_collection: LightcurveCollection
                                                          ) -> tf.data.Dataset:
        """
        Generates a paths dataset for a lightcurve collection.

        :param lightcurve_collection: The lightcurve collection to generate a paths dataset for.
        :return: The paths dataset.
        """
        paths_dataset = self.paths_dataset_from_list_or_generator_factory(lightcurve_collection.get_lightcurve_paths)
        repeated_paths_dataset = paths_dataset.repeat()
        shuffled_paths_dataset = repeated_paths_dataset.shuffle(self.shuffle_buffer_size)
        return shuffled_paths_dataset

    def generate_paths_datasets_from_lightcurve_collection_list(self, lightcurve_collections: List[LightcurveCollection]
                                                                ) -> List[tf.data.Dataset]:
        """
        Generates a paths dataset for each lightcurve collection in a list.

        :param lightcurve_collections: The list of lightcurve collections.
        :return: The list of paths datasets.
        """
        return [self.generate_paths_dataset_from_lightcurve_collection(lightcurve_collection)
                for lightcurve_collection in lightcurve_collections]

    def generate_standard_lightcurve_and_label_dataset(
            self, paths_dataset: tf.data.Dataset,
            load_from_path_function: Callable[[Path], Tuple[np.ndarray, np.ndarray]], label: float):
        pass
        # lightcurve_validation_dataset = map_py_function_to_dataset(zipped_validation_paths_dataset,
        #                                                            self.positive_injection_negative_injection_and_explicit_negative_injection_preprocessing,
        #                                                            self.number_of_parallel_processes_per_map,
        #                                                            output_types=output_types,
        #                                                            output_shapes=output_shapes,
        #                                                            flat_map=True)

    def preprocess_standard_lightcurve(self, load_from_path_function: Callable[[Path], Tuple[np.ndarray, np.ndarray]],
                                       label: float, lightcurve_path_tensor: tf.Tensor) -> (np.ndarray, np.ndarray):
        """
        Preprocesses a individual standard lightcurve from a lightcurve path tensor, using a passed function defining
        how to load the values from the lightcurve file and the label value to use. Designed to be used with `partial`
        to prepare a function which will just require the lightcurve path tensor, and can then be mapped to a dataset.

        :param load_from_path_function: The function to load the lightcurve times and fluxes from a file.
        :param label: The label to assign to the lightcurve.
        :param lightcurve_path_tensor: The tensor containing the path to the lightcurve file.
        :return: The example and label arrays shaped for use as single example for the network.
        """
        lightcurve_path = lightcurve_path_tensor.numpy().decode('utf-8')
        times, fluxes = load_from_path_function(lightcurve_path)
        fluxes = self.flux_preprocessing(fluxes)
        example = np.expand_dims(fluxes, axis=-1)
        return example, np.array([label])

    def flux_preprocessing(self, fluxes: np.ndarray, evaluation_mode: bool = False, seed: int = None) -> np.ndarray:
        """
        Preprocessing for the flux.

        :param fluxes: The flux array to preprocess.
        :param evaluation_mode: If the preprocessing should be consistent for evaluation.
        :param seed: Seed for the randomization.
        :return: The preprocessed flux array.
        """
        normalized_fluxes = self.normalize(fluxes)
        uniform_length_fluxes = self.make_uniform_length(normalized_fluxes, self.time_steps_per_example,
                                                         randomize=not evaluation_mode, seed=seed)
        return uniform_length_fluxes
