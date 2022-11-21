import logging
import copy
import pydash
import jsonschema

from json_logic import jsonLogic

from webapp.apps.skurge.models import RelayProcessor, DataProcessor
from webapp.apps.skurge.constants import RelayType
from webapp.apps.skurge.common.util import HttpUtil
from webapp.apps.skurge.services.log import RelayLogService
from webapp.apps.skurge.clients.graphql import GraphQLClient
from webapp.apps.skurge.clients.event import RabbitMQClient
from webapp.apps.skurge.serializers.relay_processor import RelayProcessorSerializer
from webapp.apps.skurge.serializers.data_processor import DataProcessorSerializer


class RelayEventProcessor:
    event = None
    endpoint = None
    http_method = None
    headers = {}
    source_data = {}
    relay_data = {}
    external_data = {}

    def fetch_relay_processors(self, source_event_id):
        """
        Fetches corresponding relay processors for the source event
        :param source_event_id:
        :return:
        """
        relay_processors = RelayProcessor.objects.filter(source_event_id=source_event_id, is_active=True,
                                                         is_deleted=False).all()
        if relay_processors:
            return RelayProcessorSerializer(instance=relay_processors, many=True).data
        return None

    def process_relayer(self, relay_processor, source_data, source_event):
        """
        Prepares the relay data, evaluates the endpoint or event and publishes it to the relayed system
        :param relay_processor:
        :param source_data:
        :param source_event:
        :return:
        """
        # Input data becomes part of out external data which can later be used as context data for payload preparation
        # or destination logic in case of API endpoint dynamic fields or finding the event name
        self.source_data = source_data
        self.external_data = copy.deepcopy(self.source_data)

        data_processor = self.get_data_processor(relay_processor=relay_processor)
        if data_processor:
            self.fetch_external_data_from_graphql_server(data_processor=data_processor)
        logging.info("External data has been prepared")

        if not self.prepare_relay_data(relay_processor=relay_processor, data_processor=data_processor,
                                       source_event=source_event):
            return
        if not self.find_destination(relay_processor=relay_processor, source_event=source_event):
            return

        self.publish(relay_processor=relay_processor)
        destination = self.event if self.event else self.endpoint
        logging.info("Message has been relayed to %s", destination)
        RelayLogService().log(source=source_event, relay_data=self.relay_data, destination=destination,
                              relay_type=relay_processor.get("relay_type"), status="SUCCESS")

    def get_data_processor(self, relay_processor):
        """
        Gets the data processor for the relay processor
        If no relay data is required then data processor can be null for that relay processor provided event name
        or api generation can be carried out by input data
        :param relay_processor:
        :return:
        """
        data_processor_id = relay_processor.get("data_processor_id")
        if not data_processor_id:
            return None

        data_processor = DataProcessor.objects.filter(id=data_processor_id).first()
        if data_processor:
            return DataProcessorSerializer(instance=data_processor, many=False).data
        return None

    def fetch_external_data_from_graphql_server(self, data_processor):
        """
        Gets the external data from graphql server if graphql query is present and updates it in the external data dict
        Graphql query would be present if you need external data for either of the three cases
        1. Relay data preparation
        2. Event name generation
        3. Dynamic url generation
        :param data_processor:
        :return:
        """
        if data_processor.get("graphql_query"):
            graphql_data = GraphQLClient().fetch_data(query=data_processor.get("graphql_query"),
                                                      variables=self.source_data)
            self.external_data.update(graphql_data)

    def prepare_relay_data(self, relay_processor, data_processor, source_event):
        """
        Prepares the relay data to be forwarded and validates it.
        If input data will be the relay data itself and no need to fetch externally ie graphql query will be empty but
        relay fields locator should be present be extract out relay data from external data
        :param relay_processor:
        :param data_processor:
        :param source_event:
        :return:
        """
        self.relay_data = {}
        if not data_processor:
            return True

        # Checks if relay data is required or not else keeps it empty
        if data_processor.get("relay_data_locator"):
            relay_fields = self.__get_relay_fields(data_processor.get("relay_data_locator"))
            if not relay_fields:
                message = "No conditions matched to get the relay fields/output fields mapper"
                logging.warning(message)
                RelayLogService().log(source=source_event, relay_data=self.relay_data, status="FAILED",
                                      reason=message, relay_type=relay_processor.get("relay_type"))
                return False
            self.extract_relay_data(mapper=relay_fields)
            self.add_static_data(data_processor=data_processor)
            error_messages = self.validate_relay_data(data_processor=data_processor)
            if error_messages:
                message = ','.join(error_messages)
                logging.warning(message)
                RelayLogService().log(source=source_event, relay_data=self.relay_data, status="FAILED",
                                      reason=message, relay_type=relay_processor.get("relay_type"))
                return False
        return True

    def __get_relay_fields(self, relay_field_rules):
        """
        Uses the relay data locator(json logic) to extract out the actual relay fields
        :param relay_field_rules:
        :return:
        """
        return jsonLogic(relay_field_rules, self.external_data)

    def extract_relay_data(self, mapper):
        """
        Uses the relay fields locator which is a dictionary of
        1. key path for the final output payload
        2. value path to extract out from the external data
        With this an output payload can be created which is nested and it can parse any level deep in the external data
        looking for values
        :param mapper:
        :return:
        """
        for key_path, value_path in mapper.items():
            value = pydash.get(self.external_data, value_path, default=value_path)
            pydash.set_(self.relay_data, key_path, value)

    def add_static_data(self, data_processor):
        """
        Adds default values to the final destination payload
        :param data_processor:
        :return:
        """
        static_data = data_processor.get("default_response")
        if static_data:
            for key_path, value in static_data.items():
                if isinstance(value, str):
                    value = value.format(**self.external_data)  # Supports dynamic string formatting
                pydash.set_(self.relay_data, key_path, value)

    def validate_relay_data(self, data_processor):
        """
        Validates the destination data using the validator object
        :param data_processor:
        :return:
        """
        validator = jsonschema.Draft7Validator(data_processor.get("relay_json_schema"))
        errors = validator.iter_errors(self.relay_data)
        error_info = []
        for error in errors:
            if hasattr(error, "message"):
                error_info.append(error.message)
        if error_info:
            logging.warning("Request Validation Failed. %s", error_info)
            return error_info
        logging.info("Relay data validated.")
        return None

    def find_destination(self, relay_processor, source_event):
        """
        Based on the relay type it either fetches the endpoint or decides on the event to raise for the destination
        :param relay_processor:
        :param source_event:
        :return:
        """
        if relay_processor.get("relay_type") == RelayType.API.value:
            # Get the context data for running jsonLogic to determine the http endpoint and to fill the dynamic part of
            # the endpoint if necessary
            context_data = self.get_context_data(relay_processor=relay_processor)

            # Run json logic to determine the destination endpoint to be called
            http_endpoint_map = self.process_http_endpoint_rules(relay_processor=relay_processor,
                                                                 context_data=context_data)
            if http_endpoint_map:
                unformatted_endpoint = http_endpoint_map.get("http_endpoint", None)
                self.http_method = http_endpoint_map.get("http_method", None)
                self.headers = http_endpoint_map.get("headers", None)
                # Add the dynamic part of the url from the context data
                self.endpoint = unformatted_endpoint.format(**context_data)

            if not (http_endpoint_map and self.endpoint and self.http_method and self.headers):
                message = "No valid endpoint, http request or headers found for the source event %s" % source_event
                logging.warning(message)
                RelayLogService().log(source=source_event, relay_data=self.relay_data, status="FAILED", reason=message,
                                      relay_type=relay_processor.get("relay_type"))
                return False
        elif relay_processor.get("relay_type") == RelayType.EVENT.value:
            if not relay_processor.get("relay_event_rules"):
                message = "Event rules not present in relay processor %s" % relay_processor.get("id")
                logging.warning(message)
                RelayLogService().log(source=source_event, status="FAILED", relay_data=self.relay_data, reason=message,
                                      relay_type=relay_processor.get("relay_type"))
                return False

            self.event = self.process_relay_rules(relay_processor=relay_processor)
            if not self.event:
                message = "No valid relay event found for the source event %s" % source_event
                logging.warning(message)
                RelayLogService().log(source=source_event, relay_data=self.relay_data, status="FAILED", reason=message,
                                      relay_type=relay_processor.get("relay_type"))
                return False
        return True

    def process_http_endpoint_rules(self, relay_processor, context_data):
        """
        Decides the api endpoint to call for the destination based on json logic rules
        If no context data is required to run json logic rules then context_data_locator can be null
        :param relay_processor:
        :param context_data:
        :return:
        """
        return jsonLogic(relay_processor.get("relay_http_endpoint_rules"), context_data)

    def process_relay_rules(self, relay_processor):
        """
        Decides the event to raise for the destination using json logic rules
        If no context data is required to run jsonlogic rules then context_data_locator can be null
        :param relay_processor:
        :return:
        """
        context_data = self.get_context_data(relay_processor=relay_processor)
        return jsonLogic(relay_processor.get("relay_event_rules"), context_data)

    def get_context_data(self, relay_processor):
        """
        Creates the context data for running the json logic rules to find the destination event
        :param relay_processor:
        :return:
        """
        context_data = {}
        for field, path in relay_processor.get("context_data_locator").items():
            value = pydash.get(self.external_data, path)
            context_data[field] = value
        return context_data

    def publish(self, relay_processor):
        """
        Publishes the event or hits the end point for the destination
        :param relay_processor:
        :return:
        """
        if relay_processor.get("relay_type") == RelayType.EVENT.value:
            RabbitMQClient().publish(self.event, self.relay_data)
        elif relay_processor.get("relay_type") == RelayType.API.value:
            HttpUtil().publish_message(url=self.endpoint, http_method=self.http_method, data=self.relay_data,
                                       headers=self.headers)
