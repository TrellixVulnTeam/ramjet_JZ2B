"""
Code for a lightcurve collection that stores its metadata in the SQL database.
"""
import random
from pathlib import Path
from typing import Iterable, List
from uuid import uuid4

from peewee import Select, Field, Case

from ramjet.data_interface.metadatabase import MetadatabaseModel
from ramjet.photometric_database.lightcurve_collection import LightcurveCollection, \
    LightcurveCollectionMethodNotImplementedError


class SqlMetadataLightcurveCollection(LightcurveCollection):
    """
    Class for a lightcurve collection that stores its metadata in the SQL database.
    """
    def __init__(self):
        super().__init__()

    def get_sql_query(self) -> Select:
        """
        Gets the SQL query for the database models for the lightcurve collection.

        :return: The SQL query.
        """
        raise LightcurveCollectionMethodNotImplementedError

    def sql_count(self) -> int:
        """
        Gets the count of the rows returned by the SQL query.

        :return: The count.
        """
        return self.get_sql_query().count()

    def get_path_from_model(self, model: MetadatabaseModel) -> Path:
        """
        Gets the lightcurve path from the SQL database model.

        :return: The path to the lightcurve.
        """
        raise LightcurveCollectionMethodNotImplementedError

    def get_paths(self) -> Iterable[Path]:
        """
        Gets the paths for the lightcurves in the collection.

        :return: An iterable of the lightcurve paths.
        """
        query = self.get_sql_query()
        query = query.iterator().objects()  # Disable Peewee's cache and graph for better performance.
        for model in query:
            yield Path(self.get_path_from_model(model))

    @staticmethod
    def order_by_uuid_with_random_start(select_query: Select, uuid_field: Field) -> Select:
        """
        Applies an "order by" on a query using a passed UUID field. The "order by" starts at a random UUID and then
        loops back to the minimum UUID include all entities.

        :param select_query: The query to add the "order by" to.
        :param uuid_field: The UUID field to order on.
        :return: The query updated to include the "order by".
        """
        random_start_case = Case(None, [(uuid_field > uuid4(), 0)], 1)
        updated_select_query = select_query.order_by(random_start_case, uuid_field)
        return updated_select_query

    @staticmethod
    def order_by_dataset_split_with_random_start(select_query: Select, dataset_split_field: Field,
                                                 available_dataset_splits: List[int]) -> Select:
        """
        Applies an "order by" on a query using a passed dataset_split field. The "order by" starts at a random
        dataset_split out of the passed available options, then loops back to the minimum dataset_split to include all
        entities.

        :param select_query: The query to add the "order by" to.
        :param dataset_split_field: The dataset_split field to order on.
        :param available_dataset_splits: The available dataset_splits to start on.
        :return: The query updated to include the "order by".
        """
        start_dataset_split = random.choice(available_dataset_splits)
        start_case = Case(None, [(dataset_split_field >= start_dataset_split, 0)], 1)
        updated_select_query = select_query.order_by(start_case, dataset_split_field)
        return updated_select_query
