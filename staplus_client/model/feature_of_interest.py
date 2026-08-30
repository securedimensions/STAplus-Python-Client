from frost_sta_client.model import feature_of_interest
from staplus_client.dao.features_of_interest import FeaturesOfInterestDao
from staplus_client.model.ext.datatypes import (
    ENCODING_TYPE_GEOJSON,
    ENCODING_TYPE_GEOJSON_VND,
    ENCODING_TYPE_JSON_FG,
    ENCODING_TYPE_WKT,
    ENCODING_TYPES,
    check_encoding_type,
)

class FeatureOfInterest(feature_of_interest.FeatureOfInterest):

    ENCODING_TYPE_GEOJSON = ENCODING_TYPE_GEOJSON
    ENCODING_TYPE_GEOJSON_VND = ENCODING_TYPE_GEOJSON_VND
    ENCODING_TYPE_JSON_FG = ENCODING_TYPE_JSON_FG
    ENCODING_TYPE_WKT = ENCODING_TYPE_WKT
    ENCODING_TYPES = ENCODING_TYPES

    @property
    def encoding_type(self):
        return self._encoding_type

    @encoding_type.setter
    def encoding_type(self, value):
        self._encoding_type = check_encoding_type(value)


    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity

    def get_observations(self):
        result = self.service.observations()
        result.parent = self
        return result

    def get_dao(self, service):
        return FeaturesOfInterestDao(service)