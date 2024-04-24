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

from frost_sta_client.model import multi_datastream
from secd_staplus_client import utils
from secd_staplus_client.model.ext import entity_list, entity_type
from secd_staplus_client.dao.multi_datastream import MultiDatastreamDao
from secd_staplus_client.model import license, campaign, party

class MultiDatastream(multi_datastream.MultiDatastream):
    def __init__(self,
                 name='',
                 description='',
                 properties=None,
                 unit_of_measurements=None,
                 observation_type='',
                 multi_observation_data_types=None,
                 observed_area=None,
                 phenomenon_time=None,
                 result_time=None,
                 thing=None,
                 sensor=None,
                 observed_properties=None,
                 observations=None,
                 campaigns=None,
                 party=None,
                 license=None,
                 **kwargs):
        super().__init__(**kwargs)
        if properties is None:
            properties = {}
        if multi_observation_data_types is None:
            multi_observation_data_types = []
        self.name = name
        self.description = description
        self.properties = properties
        self.unit_of_measurements = unit_of_measurements
        self.observation_type = observation_type
        self.multi_observation_data_types = multi_observation_data_types
        self.observed_area = observed_area
        self.phenomenon_time = phenomenon_time
        self.result_time = result_time
        self.thing = thing
        self.sensor = sensor
        self.observed_properties = observed_properties
        self.observations = observations
        self.party = party
        self.license = license
        self.campaigns = campaigns

    def __new__(cls, *args, **kwargs):
        new_mds = super().__new__(cls)
        attributes = dict(_id=None, _name='', _description='', _properties={}, _observation_type='',
                          _multi_observation_data_types=[],
                          _unit_of_measurements=[], _observed_area=None, _phenomenon_time=None, _result_time=None,
                          _thing=None, _sensor=None, _observed_properties=None, _observations=None,
                          _campaigns=None, _party=None, _license=None,
                          _self_link='', _service=None)
        for key, value in attributes.items():
            new_mds.__dict__[key] = value
        return new_mds

    @property
    def party(self):
        return self._party

    @party.setter
    def party(self, value):
        if value is None or isinstance(value, party.Party):
            self._party = value
            return
        raise ValueError('party should be of type Party!')

    def get_party(self):
        result = self.service.party()
        result.parent = self
        return result

    @property
    def license(self):
        return self._license

    @license.setter
    def license(self, value):
        if value is None or isinstance(value, license.License):
            self._license = value
            return
        raise ValueError('license should be of type License!')

    def get_license(self):
        result = self.service.license()
        result.parent = self
        return result

    def get_thing(self):
        result = self.service.thing()
        result.parent = self
        return result

    def get_sensor(self):
        result = self.service.sensor()
        result.parent = self
        return result

    @property
    def campaigns(self):
        return self._campaigns

    @campaigns.setter
    def campaigns(self, values):
        if values is None:
            self._campaigns = None
            return
        if isinstance(values, list) and all(isinstance(ps, campaign.Campaign) for ps in values):
            entity_class = entity_type.EntityTypes['Campaign']['class']
            self._campaigns = entity_list.EntityList(entity_class=entity_class, entities=values)
            return
        if not isinstance(values, entity_list.EntityList) or \
                any((not isinstance(ps, campaign.Campaign)) for ps in values.entities):
            raise ValueError('campaigns should be a list of Campaign')
        self._campaigns = values

    def get_campaigns(self):
        result = self.service.campaigns()
        result.parent = self
        return result

    def ensure_service_on_children(self, service):
        super().ensure_service_on_children(service)
        if self.party is not None:
            self.party.set_service(service)
        if self.license is not None:
            self.license.set_service(service)
        if self.campaigns is not None:
            self.campaigns.set_service(service)

    def __getstate__(self):
        data = super().__getstate__()
        if self.party is not None:
            data['Party'] = self.party
        if self.license is not None:
            data['License'] = self.license
        if self._campaigns is not None and len(self.campaigns.entities) > 0:
            data['Campaigns'] = self.campaigns.__getstate__()

        return data

    def __setstate__(self, state):
        super().__setstate__(state)
        if state.get("Party", None) is not None:
            self.party = party.Party()
            self.party.__setstate__(state["Party"])
        if state.get("License", None) is not None:
            self.license = license.License()
            self.license.__setstate__(state["License"])
        if state.get("Campaigns", None) is not None and isinstance(state["Campaigns"], list):
            entity_class = entity_type.EntityTypes['Campaign']['class']
            self.campaigns = utils.transform_json_to_entity_list(state['Campaigns'], entity_class)
            self.campaigns.next_link = state.get("Campaigns@iot.nextLink", None)
            self.campaigns.count = state.get("Campaigns@iot.count", None)

    def get_dao(self, service):
        return MultiDatastreamDao(service)
