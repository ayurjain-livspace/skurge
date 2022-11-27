# Skurge APIs #

### Table of Contents
* [API definitions](#API-definitions)
* [OpenAPI Specification](#OpenAPI-Specification)
* [Postman collection](#Postman-collection)

## API definitions
Skurge offers following APIs:

| API                                                                   | Remarks                                                                                                               |
|:----------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------|
| POST `api/v1/register-event`                                          | Registers an event (ie. data processing and relaying) in `source_events` table                                        |
| GET `api/v1/registered-event/<int:event_id>`                          | Gets event corresponding to `event_id` and all its data & relay processors                                            |
| PUT `api/v1/registered-event/<int:event_id>`                          | Updates `source_events` table                                                                                         |
| GET `api/v1/registered-events`                                        | Gets all events registered in skurge                                                                                  |
| POST `api/v1/registered-event/<int:event_id>/relayer`                 | Adds relay and data processor to the registered event ie. adds data in `data_processors` and `relay_processors` table |
| GET `api/v1/registered-event/<int:event_id>/relayer/<int:relayer_id>` | Gets relay and data processor of the registered event                                                                 |
| PUT `api/v1/registered-event/<int:event_id>/relayer/<int:relayer_id>` | Updates relay or corresponding data processor of the registered event                                                 |
| POST `api/v1/relay-event/<slug:event_name>`                           | Processes incoming events and relays it to appropriate system                                                         |


## OpenAPI Specification
OpenAPI specification for above APIs can be found in the resources folder: [OpenAPI Specs](skurge_openapi_specs.yaml).
<br />You may visualise this yaml file at [editor.swagger.io](https://editor.swagger.io/) 


## Postman collection
* The postman collection for the APIs can be found in the resources folder: [Postman Collection](skurge.postman_collection.json). You can import the json file in postman. 
* The collection uses [sample data](../webapp/apps/skurge/tests/common/constants.py) used in integration tests.
