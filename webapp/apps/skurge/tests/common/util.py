from webapp.apps.skurge.tests.common.constants import TestData
from webapp.apps.skurge.models import SourceEvent, DataProcessor, RelayProcessor
from webapp.apps.skurge.constants import RelayType


def mocked_get_data_from_graphql(*args, **kwargs):
    """
    Helper method to mock graphql response in tests.
    @param args:
    @param kwargs:
    @return:
    """
    graphql_data = {
        "userDetails": {
            "name": "aj",
            "email": "aj@abc.com",
            "country_code": "IN"
        }
    }
    return graphql_data


def mocked_publish(*args, **kwargs):
    """
    Helper method to mock publishing to rabbitmq or making http call.
    @param args:
    @param kwargs:
    @return:
    """
    return


def add_sample_data(relay_type=None):
    """
    Helper method to add source_event, data_processor & relay_processor in test db.
    @param relay_type:
    @return:
    """
    source_event_data = add_sample_source_event()
    data_processor_data = add_sample_data_processor()
    relay_processor_data = add_sample_relay_processor(source_event_id=source_event_data['id'],
                                                      data_processor_id=data_processor_data['id'], relay_type=relay_type)
    return source_event_data, data_processor_data, relay_processor_data


def add_sample_source_event():
    """
    Helper method to add source_event in test db.
    @return:
    """
    source_event_data = TestData.get_source_event()
    source_event = SourceEvent.objects.create(**source_event_data)
    source_event_data['id'] = source_event.id
    return source_event_data


def add_sample_data_processor():
    """
    Helper method to add data_processor in test db.
    @return:
    """
    data_processor_data = TestData.get_data_processor()
    data_processor = DataProcessor.objects.create(**data_processor_data)
    data_processor_data['id'] = data_processor.id
    return data_processor_data


def add_sample_relay_processor(source_event_id, data_processor_id, relay_type=None):
    """
    Helper method to add relay_processor in test db.
    @param source_event_id:
    @param data_processor_id:
    @param relay_type:
    @return:
    """
    relay_processor_data = TestData.get_relay_processor(source_event_id, data_processor_id, relay_type)
    relay_processor = RelayProcessor.objects.create(**relay_processor_data)
    relay_processor_data['id'] = relay_processor.id
    return relay_processor_data


def update_data_processor(data_processor_id, update_data):
    """
    Helper method to update data_processor in test db.
    @param data_processor_id:
    @param update_data:
    @return:
    """
    data_processor = DataProcessor.objects.filter(id=data_processor_id).first()
    if not data_processor:
        raise Exception('No data_processor found')
    for key, value in update_data.items():
        setattr(data_processor, key, value)
    data_processor.save()


def update_relay_processor(relay_processor_id, update_data):
    """
    Helper method to update relay_processor in test db.
    @param relay_processor_id:
    @param update_data:
    @return:
    """
    relay_processor = RelayProcessor.objects.filter(id=relay_processor_id).first()
    if not relay_processor:
        raise Exception('No relay_processor found')
    for key, value in update_data.items():
        setattr(relay_processor, key, value)
    relay_processor.save()


def compare_source_events(source_event_1, source_event_2):
    """
    Helper method to compare two source event dictionaries
    @param source_event_1:
    @param source_event_2:
    @return:
    """
    return __compare(dict1=source_event_1, dict2=source_event_2,
                     keys=["source_event", "input_json_schema"])


def compare_data_processors(data_processor_1, data_processor_2):
    """
    Helper method to compare two data processor dictionaries
    @param data_processor_1:
    @param data_processor_2:
    @return:
    """
    return __compare(dict1=data_processor_1, dict2=data_processor_2,
                     keys=["graphql_query", "relay_data_locator", "default_response", "relay_json_schema"])


def compare_relay_processors(relay_processor_1, relay_processor_2, relay_type=None):
    """
    Helper method to compare two relay processor dictionaries
    @param relay_processor_1:
    @param relay_processor_2:
    @param relay_type:
    @return:
    """
    keys = ["relay_type", "relay_system", "context_data_locator"]
    if relay_type == RelayType.API:
        keys.append("relay_http_endpoint_rules")
    else:
        keys.append("relay_event_rules")
    return __compare(dict1=relay_processor_1, dict2=relay_processor_2, keys=keys)


def __compare(dict1, dict2, keys):
    """
    Helper method to compare two dictionaries on value of keys passed as param.
    @param dict1:
    @param dict2:
    @param keys:
    @return:
    """
    for key in keys:
        if dict1.get(key) != dict2.get(key):
            return False
    return True
