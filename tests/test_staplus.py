import time, unittest, sqlalchemy, numpy, datetime

import geojson, json
import requests
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

from geojson import Point
import secd_staplus_client as STAplus

class TestService(unittest.TestCase):
    db_container = None
    staplus_container = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_container = PostgresContainer("postgis/postgis",dbname="sensorthings",username='sensorthings',password='secret',port=5432).with_exposed_ports(5432)
        cls.db_container.start()
        db_url = cls.db_container.get_connection_url()
        print(db_url)
        engine = sqlalchemy.create_engine(cls.db_container.get_connection_url())
        with engine.begin() as connection:
            connection.execute(sqlalchemy.text('CREATE EXTENSION "uuid-ossp";'))

        db_url = 'jdbc:postgresql://host.docker.internal' + ':' + str(cls.db_container.get_exposed_port(5432)) + '/sensorthings'
        print(db_url)
        cls.staplus_container = DockerContainer("securedimensions/staplus-python-client:2.2.x") \
            .with_env('plugins_multiDatastream_enable', 'true') \
            .with_env('plugins_coreModel_idType', 'LONG') \
            .with_env('persistence_idGenerationMode_Party', 'ServerGeneratedOnly') \
            .with_env('persistence_db_driver', 'org.postgresql.Driver') \
            .with_env('persistence_db_url', db_url) \
            .with_env('persistence_db_username', 'sensorthings') \
            .with_env('persistence_db_password', 'secret') \
            .with_env('persistence_autoUpdateDatabase', 'true') \
            .with_env('plugins_staplus_enable_enforceOwnership', 'false') \
            .with_env('plugins_staplus_enable_enforceLicensing', 'false') \
            .with_env('auth_provider', '')\
            .with_exposed_ports(8080)
        cls.staplus_container.start()

    def setUp(self) -> None:
        import secd_staplus_client as staplus
        ip = self.staplus_container.get_container_host_ip()
        port = self.staplus_container.get_exposed_port(8080)
        url = 'http://' + ip + ':' + str(port) + '/FROST-Server/v1.1'
        print(url)
        self.service = staplus.STAplusService(url)
        for ix in [0,1,2,3,4]:
            try:
                with requests.get(url) as r:
                    if r.status_code != 200:
                        print("waiting for STAplus service to become ready...")
                        time.sleep(1)
                    else:
                        break
            except:
                print("waiting for STAplus service to become ready...")
                time.sleep(1)

    def test_all(self):
        party = STAplus.Party(description='The opportunistic pirate by Robert Louis Stevenson', display_name='Long John Silver', role='individual')
        self.service.create(party)

        here = STAplus.Location(name="Munich", description="a nice place", location=Point((11,47)), encoding_type='application/geo+json')
        self.service.create(here)
        thing = STAplus.Thing('Raspberrypi', 'The thing that hosts sensors')
        thing.locations = [here]
        thing.party = party
        self.service.create(thing)

        sensor = STAplus.Sensor('FT0310Temperature', 'FT0310 Temperature Sensor', 'application/pdf',
                            {'documentation': 'https://uctechnologyltd.com/product/ft0310-wifi-weather-station/'},
                            'https://nicetymeter.com/u_file/2311/08/file/NicetyMeterFT-0310-Manual.pdf')
        self.service.create(sensor)
        celsius = STAplus.UnitOfMeasurement('Celsius', 'C', 'https://qudt.org/vocab/unit/DEG_C')
        percentage = STAplus.UnitOfMeasurement('Percentage', '%', 'https://qudt.org/vocab/unit/PERCENT')
        temp = STAplus.ObservedProperty('temp', 'http://vocabs.lter-europe.net/EnvThes/22035', 'Air Temperature')
        self.service.create(temp)
        humidity = STAplus.ObservedProperty('RH', 'http://vocabs.lter-europe.net/EnvThes/21579', 'Relative Humidity')
        self.service.create(humidity)
        cc_by = self.service.licenses().find('CC_BY')

        munich = STAplus.FeatureOfInterest(name="Munich", description="a nice place", feature=Point((11,47)), encoding_type='application/geo+json')
        self.service.create(munich)
        ds = STAplus.Datastream('Air Temperature', 'Air temperature measured with the FT-0310 Weather Station',
                                'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement')
        ds.observed_property = temp
        ds.unit_of_measurement = celsius
        ds.party = party
        ds.thing = thing
        ds.license = cc_by
        ds.sensor = sensor
        self.service.create(ds)

        ds_subject = STAplus.Observation( phenomenon_time='2016-01-07T02:00:00.000+00:00', result='0.15', feature_of_interest=munich, parameters={'relation': 'subject'}, datastream=ds)
        ds_object = STAplus.Observation( phenomenon_time='2024-04-17T12:00:00.000+00:00', result='3.74', feature_of_interest=munich, parameters={'relation': 'object'}, datastream=ds)
        self.service.create(ds_subject)
        self.service.create(ds_object)

        mds = STAplus.MultiDatastream(name='Air Temperature and Humidity',
                                      description='Air temperature and humidity measured with the FT-0310 Weather Station',
                                      properties={},
                                      unit_of_measurements=[celsius, percentage],
                                      observation_type='http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_ComplexObservation',
                                      multi_observation_data_types=['http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
                                               'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement'],
                                      observed_properties=[temp, humidity],
                                      party=party,
                                      thing=thing,
                                      license=cc_by,
                                      sensor=sensor)
        self.service.create(mds)
        mds_subject = STAplus.Observation( phenomenon_time='2016-01-07T02:00:00.000+00:00', result=[0.15, 15], feature_of_interest=munich, parameters={'relation': 'subject'}, multi_datastream=mds)
        mds_object = STAplus.Observation( phenomenon_time='2024-04-17T12:00:00.000+00:00', result=[3.74, 74], feature_of_interest=munich, parameters={'relation': 'object'}, multi_datastream=mds)
        self.service.create(mds_subject)
        self.service.create(mds_object)
        #self.service.execute('post', mds.self_link + '/Observations', json=transform_entity_to_json_dict(mds_subject))
        #self.service.execute('post', mds.self_link + '/Observations', json=transform_entity_to_json_dict(mds_object))

        relation = STAplus.Relation('temp before and after', 'time related', subject=ds_subject, object=ds_object)
        self.service.create(relation)

        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        campaign = STAplus.Campaign(name="Air Quality Munich", description="Campaign to monitor air quality in Munich",
                                    classification='public', terms_of_use="Participation is at your own risk",
                                    privacy_policy="We collect your nickname", creation_time=now, start_time='2024-04-27T06:00:00+02:00',
                                    end_time='2024-04-27T18:00:00+02:00', url='https://airquality.munich', properties={'address': 'Marienplatz'},
                                    datastreams=[ds], multi_datastreams=[mds], party=party, license=cc_by)
        self.service.create(campaign)
        observation_group = STAplus.ObservationGroup(name="OG_AQM",
                                                     description="Observations for the Campaign `Air Quality Munich`",
                                                     purpose="observation group for the campaign",
                                                     terms_of_use="At your own risk",
                                                     privacy_policy="no personal data collected",
                                                     creation_time=now, end_time='2024-04-27T18:00:00+02:00',
                                                     properties={'address': 'Marienplatz'},
                                                     campaigns=[campaign],
                                                     party=party,
                                                     observations=[ds_subject, ds_object])
        self.service.create(observation_group)
        self.check_relation(relation, ds_subject, ds_object)
        self.check_observation_filter(ds_subject, ds_object)
        self.check_observation_group(ds_subject, ds_object, party, relation, observation_group)
        self.check_campaign(cc_by, party, ds, mds, observation_group, campaign)
        self.check_location(thing, here)
        self.check_datastream(ds, thing, sensor, temp, party, cc_by, ds_subject, ds_object, campaign)
        self.check_multi_datastream(mds, thing, sensor, [temp, humidity], party, cc_by, mds_subject, mds_object, campaign)
        self.check_thing(thing, ds, here, party)
        self.check_sensor(sensor, ds)
        self.check_observed_property(temp, ds)
        self.check_feature_of_interest(munich, ds_subject, ds_object)

    def check_relation(self, relation, subject, object):
        print("testing Relation")
        s = relation.get_subject().query().item()
        o = relation.get_object().query().item()
        self.assertEqual(subject, s, "Relation.Subject equals Subject")
        self.assertEqual(object, o, "Relation.Object equals Object")
        print("testing Subject relations")
        subjects = s.get_subjects().query().list()
        self.assertTrue(subjects.entities == [], "Subject.Subjects.entities must be []")
        objects = s.get_objects().query().list()
        self.assertEqual(relation, objects.entities[0], "Relation must be in Subject.Objects")

        print("testing Object relations")
        subjects = o.get_subjects().query().list()
        self.assertEqual(relation, subjects.entities[0], "Relation must be in Object.Subjects")
        objects = o.get_objects().query().list()
        self.assertTrue(objects.entities == [], "Object.Subjects.entities must be []")


        print("finished testing relations")

    def check_observation_filter(self, subject, object):
        print("testing Filter on Observations.Subjects")

        subjects = self.service.observations().query().filter("Subjects/Subject/parameters/relation eq 'subject'").list()
        print("testing object is entitylist of Subjects.Subject via Filter")
        self.assertTrue(subjects.entities[0] == object, "object should be in Subjects.Subject") #wrong?
        subjects = self.service.observations().query().filter("Objects/Subject/parameters/relation eq 'subject'").list()
        print("testing subject is entitylist of Objects.Subject via Filter")
        self.assertTrue(subjects.entities[0] == subject, "subject should be in Objects.Subject")

        objects = self.service.observations().query().filter("Objects/Object/parameters/relation eq 'object'").list()
        print("testing subject is entitylist of Objects.Object via Filter")
        self.assertTrue(objects.entities[0] == subject, "subject should be in Objects.Object") #wrong?
        objects = self.service.observations().query().filter("Subjects/Object/parameters/relation eq 'object'").list()
        print("testing object is entitylist of Subjects.Object via Filter")
        self.assertTrue(objects.entities[0] == object, "object should be in Subjects.Object")


        none = self.service.observations().query().filter("Subjects/Subject/parameters/relation eq 'object'").list()
        print("testing [] is entitylist of Subjects.Subject via Filter")
        self.assertTrue(none.entities == [], "[] should be in Subjects.Subject")
        none = self.service.observations().query().filter("Objects/Subject/parameters/relation eq 'object'").list()
        print("testing [] is entitylist of Objects.Subject via Filter")
        self.assertTrue(none.entities == [], "[] should be in Objects.Subject")

        none = self.service.observations().query().filter("Objects/Object/parameters/relation eq 'subject'").list()
        print("testing [] is entitylist of Objects.Object via Filter")
        self.assertTrue(none.entities == [], "[] should be in Objects.Object")
        none = self.service.observations().query().filter("Subjects/Object/parameters/relation eq 'subject'").list()
        print("testing [] is entitylist of Subjects.Object via Filter")
        self.assertTrue(none.entities == [], "[] should be in Subjects.Object")

    def check_observation_group(self, subject, object, party, relation, observation_group):
        print("testing ObservationGroup")
        observations = observation_group.get_observations().query().list()
        print("observations equals [subject, object]")
        self.assertTrue(numpy.array_equiv(observations.entities,[subject,object]), "observation equals [subject, object]")

        relations = observation_group.get_relations().query().list()
        print("relations equals [relation]")
        self.assertTrue(numpy.array_equiv(relations.entities, [relation]), "relations equals [subject, object]")

        ljs = observation_group.get_party().query().item()
        print("party equals party")
        self.assertEqual(ljs, party, "party equals ObservationGroups.Party")

    def check_campaign(self, license, party, datastream, multi_datastream, observation_group, campaign):
        print("testing Campaign")

        print("Campaign is linked to ObservationGroup")
        campaigns = observation_group.get_campaigns().query().list()
        self.assertEqual(campaigns.entities[0], campaign, "Campaign is linked to ObservationGroup")

        print("ObservationGroup is linked to Campaign")
        observation_groups = campaign.get_observation_groups().query().list()
        self.assertEqual(observation_groups.entities[0], observation_group, "ObservationGroup is linked to Campaign")

        print("Party is linked to Campaign")
        ljs = campaign.get_party().query().item()
        self.assertEqual(party, ljs, "Party is linked to Campaign")

        print("Campaign is linked to Party")
        campaigns = party.get_campaigns().query().list()
        self.assertEqual(campaigns.entities[0], campaign, "Campaign is linked to Party")

        print("Campaign is linked to License")
        cc_by = campaign.get_licence().query().item()
        self.assertEqual(cc_by, license, "Campaign is linked to License")

        print("License is linked to Campaign")
        campaigns = license.get_campaigns().query().list()
        self.assertEqual(campaigns.entities[0], campaign, "License is linked to Campaign")

        print("Campaign is linked to Datastream")
        datastreams = campaign.get_datastreams().query().list()
        self.assertEqual(datastreams.entities[0], datastream, "Campaign is linked to Datastream")

        print("Datastream is linked to Campaign")
        campaigns = datastream.get_campaigns().query().list()
        self.assertEqual(campaigns.entities[0], campaign, "Datastream is linked to Campaign")

        print("Campaign is linked to MultiDatastream")
        multi_datastreams = campaign.get_multi_datastreams().query().list()
        self.assertEqual(multi_datastreams.entities[0], multi_datastream, "Campaign is linked to MultiDatastream")

        print("MultiDatastream is linked to Campaign")
        campaigns = multi_datastream.get_campaigns().query().list()
        self.assertEqual(campaigns.entities[0], campaign, "MultiDatastream is linked to Campaign")

    def check_location(self, thing, location):
        print("Testing Location")

        print("Thing is linked to Location")
        locations = thing.get_locations().query().list()
        self.assertEqual(locations.entities[0], location, "Thing is linked to Location")

        print("Location is linked to Thing")
        things = location.get_things().query().list()
        self.assertEqual(things.entities[0], thing, "Location is linked to Thing")

    def check_datastream(self, datastream, thing, sensor, observed_property, party, license, o1, o2, campaign):
        print("Testing Datastream")

        print("Datastream is linked to Party")
        entity = datastream.get_party().query().item()
        self.assertEqual(entity, party, "Datastream is linked to Party")

        print("Datastream is linked to Thing")
        entity = datastream.get_thing().query().item()
        self.assertEqual(entity, thing, "Datastream is linked to Thing")

        print("Datastream is linked to Sensor")
        entity = datastream.get_sensor().query().item()
        self.assertEqual(entity, sensor, "Datastream is linked to Sensor")

        print("Datastream is linked to ObservedProperty")
        entity = datastream.get_observed_property().query().item()
        self.assertEqual(entity, observed_property, "Datastream is linked to ObservedProperty")

        print("Datastream is linked to Campaign")
        entities = datastream.get_campaigns().query().list()
        self.assertTrue(numpy.array_equiv(entities.entities, [campaign]), "Datastream is linked to Campaign")

        print("Datastream is linked to License")
        entity = datastream.get_license().query().item()
        self.assertEqual(entity, license, "Datastream is linked to License")

        print("Datastream is linked to Observations")
        entities = datastream.get_observations().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [o1, o2]), "Datastream is linked to Observations")


        print("Party is linked to Datastream")
        entities = party.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "Party is linked to Datastream")

        print("Thing is linked to Datastream")
        entities = thing.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "Thing is linked to Datastream")

        print("Sensor is linked to Datastream")
        entities = sensor.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "Sensor is linked to Datastream")

        print("ObservedProperty is linked to Datastream")
        entities = observed_property.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "ObservedProperty is linked to Datastream")

        print("Campaign is linked to Datastream")
        entities = campaign.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "Campaign is linked to Datastream")

        print("License is linked to Datastream")
        entities = license.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "License is linked to Datastream")

        print("Observations are linked to Datastream")
        entity = o1.get_datastream().query().item()
        self.assertEqual(entity, datastream, "Observation 1 is linked to Datastream")
        entity = o2.get_datastream().query().item()
        self.assertEqual(entity, datastream, "Observation 2 is linked to Datastream")

    def check_multi_datastream(self, multi_datastream, thing, sensor, observed_properties, party, license, o1, o2, campaign):
        print("Testing MultiDatastream")

        print("MultiDatastream is linked to Party")
        entity = multi_datastream.get_party().query().item()
        self.assertEqual(entity, party, "MultiDatastream is linked to Party")

        print("MultiDatastream is linked to Thing")
        entity = multi_datastream.get_thing().query().item()
        self.assertEqual(entity, thing, "MultiDatastream is linked to Thing")

        print("MultiDatastream is linked to Sensor")
        entity = multi_datastream.get_sensor().query().item()
        self.assertEqual(entity, sensor, "MultiDatastream is linked to Sensor")

        print("MultiDatastream is linked to ObservedProperty")
        entities = multi_datastream.get_observed_properties().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, observed_properties), "MultiDatastream is linked to ObservedProperty")

        print("MultiDatastream is linked to Campaign")
        entities = multi_datastream.get_campaigns().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [campaign]), "MultiDatastream is linked to Campaign")

        print("MultiDatastream is linked to License")
        entity = multi_datastream.get_license().query().item()
        self.assertEqual(entity, license, "MultiDatastream is linked to License")

        print("MultiDatastream is linked to Observations")
        entities = multi_datastream.get_observations().query().list().entities
        for o in entities:
            self.assertTrue(o in [o1, o2], "MultiDatastream is linked to Observations")


        print("Party is linked to MultiDatastream")
        entities = party.get_multi_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [multi_datastream]), "Party is linked to MultiDatastream")

        print("Thing is linked to MultiDatastream")
        entities = thing.get_multi_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [multi_datastream]), "Thing is linked to MultiDatastream")

        print("Sensor is linked to MultiDatastream")
        entities = sensor.get_multi_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [multi_datastream]), "Sensor is linked to MultiDatastream")

        print("ObservedProperty is linked to MultiDatastream")
        for observed_property in observed_properties:
            entities = observed_property.get_multi_datastreams().query().list().entities
            self.assertTrue(numpy.array_equiv(entities, [multi_datastream]), "ObservedProperty is linked to MultiDatastream")

        print("Campaign is linked to MultiDatastream")
        entities = campaign.get_multi_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [multi_datastream]), "Campaign is linked to MultiDatastream")

        print("License is linked to MultiDatastream")
        entities = license.get_multi_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [multi_datastream]), "License is linked to MultiDatastream")

        print("Observations are linked to MultiDatastream")
        entity = o1.get_multi_datastream().query().item()
        self.assertEqual(entity, multi_datastream, "Observation 1 is linked to MultiDatastream")
        entity = o2.get_multi_datastream().query().item()
        self.assertEqual(entity, multi_datastream, "Observation 2 is linked to MultiDatastream")

    def check_thing(self, thing, datastream, location, party):
        print("Testing Thing")

        print("Thing is linked with Datastream")
        entities = thing.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "Thing is linked with Datastream")

        print("Thing is linked with Party")
        entity = thing.get_party().query().item()
        self.assertEqual(entity, party, "Thing is linked with Party")

        print("Thing is linked with Location")
        entities = thing.get_locations().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [location]), "Thing is linked with Location")

        print("Thing is linked with HistoricalLocation")
        entities = thing.get_historical_locations().query().list().entities
        historical_location = entities[0]
        locations = historical_location.get_locations().query().list().entities
        self.assertTrue(numpy.array_equiv(locations, [location]), "Thing is linked with HistoricalLocation")

        print("Datastream is linked with Thing")
        entity = datastream.get_thing().query().item()
        self.assertEqual(entity, thing, "Datastream is linked with Thing")

        print("Party is linked with Thing")
        entities = party.get_things().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [thing]), "Party is linked with Thing")

        print("Location is linked with Thing")
        entities = location.get_things().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [thing]), "Location is linked with Thing")

        print("Location and Thing are linked with HistoricalLocations")
        location_historical_locations = location.get_historical_locations().query().list().entities
        thing_historical_locations = location_historical_locations[0].get_thing().query().item()
        self.assertEqual(thing_historical_locations, thing, "Location and Thing are linked with HistoricalLocations")

    def check_sensor(self, sensor, datastream):
        print("Testing Sensor")

        print("Sensor is linked with Datastream")
        entities = sensor.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "Sensor is linked with Datastream")

        print("Datastream is linked with Sensor")
        entity = datastream.get_sensor().query().item()
        self.assertEqual(entity, sensor, "Datastream is linked with Sensor")

    def check_observed_property(self, observed_property, datastream):
        print("Testing ObservedProperty")

        print("ObservedProperty is linked with Datastream")
        entities = observed_property.get_datastreams().query().list().entities
        self.assertTrue(numpy.array_equiv(entities, [datastream]), "ObservedProperty is linked with Datastream")

        print("Datastream is linked with ObservedProperty")
        entity = datastream.get_observed_property().query().item()
        self.assertEqual(entity, observed_property, "Datastream is linked with ObservedProperty")

    def check_feature_of_interest(self, foi, subject, object):
        print("Testing FeatureOfInterest")

        print("FeatureOfInterest is linked with Observation")
        entities = foi.get_observations().query().list().entities
        self.assertTrue(subject in entities, "FeatureOfInterest is linked with Observation")
        self.assertTrue(object in entities, "FeatureOfInterest is linked with Observation")

        print("Observation is linked with FeatureOfInterest")
        entity = subject.get_feature_of_interest().query().item()
        self.assertEqual(entity, foi, "Observation 1 is linked with FeatureOfInterest")
        entity = object.get_feature_of_interest().query().item()
        self.assertEqual(entity, foi, "Observation 2 is linked with FeatureOfInterest")