# OGC STAplus (Sensorthings) API Python Client

This STAplus Python Client is an extension to the [FROST API Python Client](https://github.com/FraunhoferIOSB/FROST-Python-Client). This implementation is a python package for the [STAplus](https://github.com/opengeospatial/sensorthings/tree/22-022) API and aims to simplify development of STAplus and SensorThings enabled client applications.

## Features
* Support for all STAplus and SensorThings entity types
* CRUD operations
* Queries on entity lists
* MultiDatastreams

## API

The `STAplusService` class is central to the library. An instance of it represents a STAplus service and is identified by a URI.


### CRUD operations
The source code below demonstrates the CRUD operations for Thing objects. Operations for other entities work similarly.
```python
import secd_staplus_client as staplus

url = "<your domain>/staplus/v1.1"
service = staplus.STAplusService(url)
```
#### Creating a Party Entity
The `Party` entity represents a user or an institution. When interacting with a STAplus service that has enabled authentication, the `Party` entity represents the acting user and access control controls Create, Update and Delete.
```python
import secd_staplus_client as staplus

url = "<your domain>/staplus/v1.1"
auth_handler.AuthHandler(...)
service = staPlus.STAplusService(url, auth_handler=auth)
ljs = staPlus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)
```

#### Creating a STAplus enriched Datastream
The STAplus `Datastream` is capable to have a `Party` and a `License` associated. Also, the `Thing` is associated to a `Party` entity.
```python
import secd_staplus_client as staplus

url = "<your domain>/staplus/v1.1"
auth_handler.AuthHandler(...)
service = staplus.STAplusService(url, auth_handler=auth)
ljs = staplus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)

# find the CC-BY license
cc_by = service.licenses().find('CC_BY')

# Create a thing associated to LJS
thing = staplus.Thing('Raspberry Pi', 'Raspberry Pi 4', )
thing.party = ljs

# Create a sensor
sensor = staplus.Sensor('air temperature sensor', 'SmartCitizen air temperature sensor', 'test/html', None,
                        'https://www.seeedstudio.com/Smart-Citizen-Starter-Kit-p-2865.html')

# Create a datastream associated to LJS with CC-BY license
datastream = staplus.Datastream('air temperature', 'air temperature measured with the SmartCitizen Kit',
                                'http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement', 
                                staplus.UnitOfMeasurement('Celsius', 'C', 'https://qudt.org/vocab/unit/DEG_C'))
datastream.observed_property = staplus.ObservedProperty('temperature', 'http://vocabs.lter-europe.net/EnvThes/22035',
                                            'air temperature')
datastream.party = ljs
datastream.thing = thing
datastream.sensor = sensor
datastream.license = cc_by

service.create(datastream)
```

#### Creating a few Observation entities
```python
import secd_staplus_client as staplus

url = "<your domain>/staplus/v1.1"
auth_handler.AuthHandler(...)
service = staplus.STAplusService(url, auth_handler=auth)
ljs = staplus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)

# The feature of interest
marienplatz = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [11.571831046,48.135666124]
    }
}
foi = staplus.FeatureOfInterest('Marienplatz', 'famous place in Munich', 'application/vnd.geo+json', marienplatz)

# The temperature
observation = staplus.Observation("2023-07-02T15:34:00Z", 20, "2023-07-02T15:34:00Z")
observation.feature_of_interest = foi
observation.datastream = service.datastreams().find(<the datastream id created previously>)

service.create(observation)

observation = staplus.Observation("2023-07-02T15:34:10Z", 21, "2023-07-02T15:34:10Z")
observation.feature_of_interest = foi
observation.datastream = service.datastreams().find(<the datastream id created previously>)

service.create(observation)
```

#### Creating a Group Entity
A `Group` entity can be used as a container of observations that belong together.

```python
import secd_staplus_client as staplus

url = "<your domain>/staplus/v1.1"
service = staPlus.STAplusService(url, auth_handler=auth)
ljs = staPlus.Party(description='I am Long John Silver the opportunistic pirate created by Robert Louis Stevenson',
                    display_name='LJS',
                    role='individual')
service.create(ljs)
group = staPlus.ObservationGroup("Marienplatz", "observations on Marienplatz", "none", "")
group.creation_time = parse_datetime("2023-07-02T15:35:00Z")
# Add all the observations that are associated to the FoI named 'Marienplatz'
group.observations = service.observations().query().filter("FeatureOfInterest/name eq 'Marienplatz'").list()
group.license = service.licenses().find('CC_BY')
group.party = ljs

service.create(group)
```

#### Creating SensorThings Entities
How to use this implementation on SensorThings Entity Types, please see the [FROST-Python-Client](https://github.com/securedimensions/STAplus-Python-Client) documentation.