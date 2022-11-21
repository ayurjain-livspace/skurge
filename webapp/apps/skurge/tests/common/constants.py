import copy
from webapp.apps.skurge.constants import RelayType

TEST_SOURCE_EVENT = {
    "source_event": "TEST_EVENT",
    "input_json_schema": {"type": "object", "required": ["user_id"], "properties": {"user_id": {"type": "integer"}}}
}

TEST_DATA_PROCESSOR = {
    "graphql_query": "query get_data($user_id: ID!) { userDetails(user_id: $user_id) { name email country_code } }",
    "relay_data_locator": {"if": [{"==": [{"var": "userDetails.country_code"}, "IN"]}, {"template_id": "email-template-for-india", "template_data.name": "userDetails.name"}, {"template_id": "email-template-for-others", "template_data.name": "userDetails.name"}]},
    "default_response": {"from": "care@abc.com", "to": "{userDetails[email]}"},
    "relay_json_schema": {"type": "object", "required": ["from", "to"], "properties": {"from": {"type": "string"}, "to": {"type": "string"}}}
}

TEST_RELAY_PROCESSOR_RELAY_TYPE_EVENT = {
    "relay_type": "EVENT",
    "relay_system": "notification-service",
    "relay_event_rules": {"if": [{"==": [1, 1]}, "SEND_EMAIL"]},
    "context_data_locator": {}
}

TEST_RELAY_PROCESSOR_RELAY_TYPE_API = {
    "relay_type": "API",
    "relay_system": "external-service",
    "context_data_locator": {"country_code": "userDetails.country_code"},
    "relay_http_endpoint_rules": {"if": [{"==": [{"var": "country_code"}, "IN"]}, {"headers": {"Content-Type": "application/json"}, "http_method": "post", "http_endpoint": "https://api.abc.com/pqr"}]},
}


class TestData:
    """
        Sample data used in tests.
    """
    @staticmethod
    def get_source_event():
        return copy.deepcopy(TEST_SOURCE_EVENT)

    @staticmethod
    def get_data_processor():
        return copy.deepcopy(TEST_DATA_PROCESSOR)

    @staticmethod
    def get_relay_processor(source_event_id=None, data_processor_id=None, relay_type=None):
        if relay_type == RelayType.API:
            relay_processor_data = copy.deepcopy(TEST_RELAY_PROCESSOR_RELAY_TYPE_API)
        else:
            relay_processor_data = copy.deepcopy(TEST_RELAY_PROCESSOR_RELAY_TYPE_EVENT)
        if source_event_id is not None:
            relay_processor_data['source_event_id'] = source_event_id
        if data_processor_id is not None:
            relay_processor_data['data_processor_id'] = data_processor_id
        return relay_processor_data
