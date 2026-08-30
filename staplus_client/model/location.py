from frost_sta_client.model import location
from staplus_client.dao.location import LocationDao
from staplus_client.model.ext.datatypes import (
    ENCODING_TYPE_GEOJSON,
    ENCODING_TYPE_GEOJSON_VND,
    ENCODING_TYPE_JSON_FG,
    ENCODING_TYPE_WKT,
    ENCODING_TYPES,
    check_encoding_type,
)

class Location(location.Location):

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
    
    def get_things(self):
        result = self.service.things()
        result.parent = self
        return result
    
    def get_historical_locations(self):
        result = self.service.historical_locations()
        result.parent = self
        return result

    def get_dao(self, service):
        return LocationDao(service)