# Copyright (C) 2023 Secure Dimensions GmbH, Munich, Germany.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from secd_staplus_client import model
from secd_staplus_client import dao
from secd_staplus_client import service
from secd_staplus_client import query

from secd_staplus_client.model.party import Party
from secd_staplus_client.model.license import License
from secd_staplus_client.model.thing import Thing
from secd_staplus_client.model.datastream import Datastream
from secd_staplus_client.model.multi_datastream import MultiDatastream
from secd_staplus_client.model.campaign import Campaign
from secd_staplus_client.model.relation import Relation
from secd_staplus_client.model.observation_group import ObservationGroup
from secd_staplus_client.model.observation import Observation
from secd_staplus_client.model.feature_of_interest import FeatureOfInterest
from secd_staplus_client.model.location import Location

from secd_staplus_client.service.staplusservice import STAplusService
from secd_staplus_client.model.ext.entity_type import EntityTypes

from secd_staplus_client.utils import transform_json_to_entity_list
from frost_sta_client.model.sensor import Sensor
from frost_sta_client.model.observedproperty import ObservedProperty
from frost_sta_client.model.ext.unitofmeasurement import UnitOfMeasurement
from frost_sta_client.model.historical_location import HistoricalLocation


import jsonpickle

jsonpickle.load_backend('demjson3', 'encode', 'decode', 'JSONDecodeError')
jsonpickle.set_preferred_backend('demjson3')
jsonpickle.set_decoder_options("demjson3", decode_float=float)

from .__version__ import (__title__, __version__, __license__, __author__, __contact__, __url__,
                          __description__, __copyright__)
