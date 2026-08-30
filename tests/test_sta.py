import time, unittest, sqlalchemy, numpy, datetime, geojson, json, requests, sys, logging

from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

from geojson import Point
import staplus_client as STAplus
from staplus_client.utils import transform_entity_to_json_dict

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger()

#This is for MAC
USE_DOCKER_HOST_INTERNAL = True

class TestService(unittest.TestCase):
    db_container = None
    STAplus_container = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_container = PostgresContainer("postgis/postgis",dbname="sensorthings",username='sensorthings',password='secret',port=5432).with_exposed_ports(5432)
        cls.db_container.start()
        db_url = cls.db_container.get_connection_url()
        logger.debug(db_url)
        engine = sqlalchemy.create_engine(cls.db_container.get_connection_url())
        with engine.begin() as connection:
            connection.execute(sqlalchemy.text('CREATE EXTENSION "uuid-ossp";'))

        if USE_DOCKER_HOST_INTERNAL:
            db_url = 'jdbc:postgresql://host.docker.internal' + ':' + str(cls.db_container.get_exposed_port(5432)) + '/sensorthings'
        else:
            docker_id = cls.db_container.get_docker_client().client.api.containers()[0]['Id']
            docker_ip = cls.db_container.get_docker_client().gateway_ip(docker_id)
            #docker_ip = cls.db_container.get_docker_client().client.api.containers()[0]['NetworkSettings']['Networks']['bridge']['IPAddress']
            db_url = 'jdbc:postgresql://' + docker_ip + ':' + str(cls.db_container.get_exposed_port(5432)) + '/sensorthings'

        logger.debug(db_url)
        cls.STAplus_container = DockerContainer("fraunhoferiosb/frost-server:latest") \
            .with_env('plugins_multiDatastream_enable', 'true') \
            .with_env('plugins_coreModel_idType', 'LONG') \
            .with_env('persistence_idGenerationMode_Party', 'ServerGeneratedOnly') \
            .with_env('persistence_db_driver', 'org.postgresql.Driver') \
            .with_env('persistence_db_url', db_url) \
            .with_env('persistence_db_username', 'sensorthings') \
            .with_env('persistence_db_password', 'secret') \
            .with_env('persistence_autoUpdateDatabase', 'true') \
            .with_env('serviceRootUrl', 'http://localhost:8080/FROST-Server/v1.1')\
            .with_exposed_ports(8080)
        cls.STAplus_container.start()

    def setUp(self) -> None:
        ip = self.STAplus_container.get_container_host_ip()
        port = self.STAplus_container.get_exposed_port(8080)
        url = 'http://' + ip + ':' + str(port) + '/FROST-Server/v1.1'
        logger.debug(url)
        self.service = STAplus.STAplusService(url)
        for ix in [0,1,2,3,4,5,6,7,8,9]:
            try:
                with requests.get(url) as r:
                    if r.status_code != 200:
                        logger.debug("waiting for STAplus service to become ready...")
                        time.sleep(1)
                    else:
                        break
            except:
                logger.debug("waiting for STAplus service to become ready...")
                time.sleep(2)

    def test_all(self):
        # Location
        here = STAplus.Location(name="Munich", description="a nice place", location=Point((11,47)), encoding_type='application/geo+json', properties={'name': 'Munich'})
        self.service.create(here)

        # Thing
        raspi = STAplus.Thing('Raspberrypi', 'The thing that hosts sensors', properties={'type': '4'})
        raspi.locations = [here]
        self.service.create(raspi)
        logger.debug(f"raspi: {json.dumps(transform_entity_to_json_dict(raspi))}")

        # Sensor
        temp_humidity_sensor = STAplus.Sensor('FT0310Temperature', 'FT0310 Temperature Sensor', 'application/pdf',
                            {'documentation': 'https://uctechnologyltd.com/product/ft0310-wifi-weather-station/'},
                            'https://nicetymeter.com/u_file/2311/08/file/NicetyMeterFT-0310-Manual.pdf')
        temp_humidity_sensor.properties = {'type': '4711'}
        self.service.create(temp_humidity_sensor)
        logger.debug(f"temp_humidity_sensor: {json.dumps(transform_entity_to_json_dict(temp_humidity_sensor))}")

        # Unit of measurement CELSIUS
        celsius = STAplus.UnitOfMeasurement('Celsius', 'C', 'https://qudt.org/vocab/unit/DEG_C')
        percentage = STAplus.UnitOfMeasurement('Percentage', '%', 'https://qudt.org/vocab/unit/PERCENT')
        temp = STAplus.ObservedProperty('temp', 'http://vocabs.lter-europe.net/EnvThes/22035', 'Air Temperature')
        self.service.create(temp)
        logger.debug(f"temp: {json.dumps(transform_entity_to_json_dict(temp))}")

        # Unit of measurement RELATIVE HUMIDITY
        humidity = STAplus.ObservedProperty('RH', 'http://vocabs.lter-europe.net/EnvThes/21579', 'Relative Humidity')
        self.service.create(humidity)
        logger.debug(f"humidity: {json.dumps(transform_entity_to_json_dict(humidity))}")

        # Create the Feature of Interest
        munich = STAplus.FeatureOfInterest(name="Munich", description="a nice place", feature=Point((11,47)), encoding_type='application/geo+json')
        self.service.create(munich)
        logger.debug(f"munich: {json.dumps(transform_entity_to_json_dict(munich))}")

        # Datastream Temperature
        temp_ds = STAplus.Datastream('Air Temperature', 'Air temperature measured with the FT-0310 Weather Station',
                                'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement')
        temp_ds.observed_property = temp
        temp_ds.unit_of_measurement = celsius
        temp_ds.thing = raspi
        temp_ds.sensor = temp_humidity_sensor
        temp_ds.properties = {'kind': 'temperature'}
        self.service.create(temp_ds)
        logger.debug(f"temp_ds: {json.dumps(transform_entity_to_json_dict(temp_ds))}")
        
        # Datastream Humidity
        humidity_ds = STAplus.Datastream('Air Temperature and Humidity', 'Air temperature and humidity measured with the FT-0310 Weather Station',
                                'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement')
        humidity_ds.observed_property = humidity
        humidity_ds.unit_of_measurement = percentage
        humidity_ds.thing = raspi
        humidity_ds.sensor = temp_humidity_sensor
        humidity_ds.properties = {'kind': 'humidity'}
        self.service.create(humidity_ds)
        logger.debug(f"humidity_ds: {json.dumps(transform_entity_to_json_dict(humidity_ds))}")

        # Multidatastream
        temp_humidity_mds = STAplus.MultiDatastream(name='Air Temperature and Humidity',
                                      description='Air temperature and humidity measured with the FT-0310 Weather Station',
                                      properties={},
                                      unit_of_measurements=[celsius, percentage],
                                      observation_type='http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_ComplexObservation',
                                      multi_observation_data_types=['http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement',
                                               'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement'],
                                      observed_properties=[temp, humidity],
                                      thing=raspi,
                                      sensor=temp_humidity_sensor)
        self.service.create(temp_humidity_mds)
        logger.debug(f"temp_humidity_mds: {json.dumps(transform_entity_to_json_dict(temp_humidity_mds))}")

        # Observation
        temp_hunidity = STAplus.Observation( phenomenon_time='2024-05-17T12:00:00.000+00:00', result=[0.15, 15], feature_of_interest=munich, parameters={'kind': 'temperature and humidity'}, multi_datastream=temp_humidity_mds)
        self.service.create(temp_hunidity)
        logger.debug(f"temp_hunidity: {json.dumps(transform_entity_to_json_dict(temp_hunidity))}")

        location = self.service.locations().find(here.id)
        self.assertEqual(location, here)
        locations = self.service.locations().query().list()
        self.assertEqual(locations.get(0), here)

        historical_locations = self.service.historical_locations().query().list()
        self.assertNotEqual(historical_locations, [])

        thing = self.service.things().find(raspi.id)
        self.assertEqual(thing, raspi)
        things = self.service.things().query().list()
        self.assertEqual(things.get(0), raspi)

        sensor = self.service.sensors().find(temp_humidity_sensor.id)
        self.assertEqual(sensor, temp_humidity_sensor)
        sensors = self.service.sensors().query().list()
        self.assertEqual(sensors.get(0), temp_humidity_sensor)

        ds = self.service.datastreams().find(temp_ds.id)
        self.assertEqual(ds, temp_ds)
        dss = self.service.datastreams().query().filter("properties/kind eq 'temperature'").list()
        self.assertEqual(dss.get(0), temp_ds)

        ds = self.service.datastreams().find(humidity_ds.id)
        self.assertEqual(ds, humidity_ds)
        dss = self.service.datastreams().query().filter("properties/kind eq 'humidity'").list()
        self.assertEqual(dss.get(0), humidity_ds)

        self.assertNotEqual(temp_ds, humidity_ds)

        mds = self.service.multi_datastreams().find(temp_humidity_mds.id)
        logger.debug(f"mds: {json.dumps(transform_entity_to_json_dict(mds))}")
        self.assertEqual(mds, temp_humidity_mds)
        mdss = self.service.multi_datastreams().query().list()
        self.assertEqual(mdss.get(0), temp_humidity_mds)

        observation = self.service.observations().find(temp_hunidity.id)
        self.assertEqual(temp_hunidity, observation)
        observations = self.service.observations().query().list()
        self.assertEqual(observations.get(0), observation)