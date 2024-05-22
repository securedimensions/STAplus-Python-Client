from staplus_client import model
from staplus_client import dao
from staplus_client import query
from staplus_client import service

from staplus_client.model.datastream import Datastream
from staplus_client.model.entity import Entity
from staplus_client.model.feature_of_interest import FeatureOfInterest
from staplus_client.model.historical_location import HistoricalLocation
from staplus_client.model.location import Location
from staplus_client.model.multi_datastream import MultiDatastream
from staplus_client.model.observation import Observation
from staplus_client.model.observedproperty import ObservedProperty
from staplus_client.model.sensor import Sensor
from staplus_client.model.thing import Thing
from staplus_client.model.ext.unitofmeasurement import UnitOfMeasurement
from staplus_client.service.staplusservice import STAplusService
from staplus_client.service.auth_handler import AuthHandler
from staplus_client.model.ext.entity_type import EntityTypes
from staplus_client.model.ext.entity_list import EntityList

import jsonpickle
import demjson3

jsonpickle.load_backend('demjson3', 'encode', 'decode', 'JSONDecodeError')
jsonpickle.set_preferred_backend('demjson3')
jsonpickle.set_decoder_options("demjson3", decode_float=float)

from .__version__ import (__title__, __version__, __license__, __author__, __contact__, __url__,
                          __description__, __copyright__)
