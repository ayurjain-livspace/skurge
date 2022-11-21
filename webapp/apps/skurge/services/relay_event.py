from webapp.apps.skurge.models import RelayProcessor, DataProcessor
from webapp.apps.skurge.constants import RelayType
from webapp.apps.skurge.common.util import ValidityUtil
from webapp.apps.skurge.common.exceptions import InvalidInputException
from webapp.apps.skurge.serializers.relay_processor import RelayProcessorSerializer
from webapp.apps.skurge.serializers.data_processor import DataProcessorSerializer


class RelayEventService:

    def get_processors_for_event(self, event_id):
        """
        Fetches all processors for the registered event
        :param event_id:
        :return:
        """
        processors = RelayProcessor.objects.filter(source_event_id=event_id, is_deleted=False, is_active=True).all()
        if not processors:
            return {}
        relay_processors = RelayProcessorSerializer(instance=processors, many=True).data
        for relay_processor in relay_processors:
            data_processor = None
            if relay_processor.get("data_processor_id"):
                data_processor = self.__get_data_processor(data_processor_id=relay_processor.get("data_processor_id"))
            relay_processor["data_processor"] = data_processor
        return relay_processors

    def get_relay_processor(self, event_id, relay_processor_id):
        """
        Fetch relay processor
        :param event_id:
        :param relay_processor_id:
        :return:
        """
        processor = RelayProcessor.objects.filter(id=relay_processor_id, source_event_id=event_id, is_deleted=False,
                                                  is_active=True).first()
        if not processor:
            raise InvalidInputException("Processor not found")
        relay_processor = RelayProcessorSerializer(instance=processor, many=False).data
        data_processor = None
        if relay_processor.get("data_processor_id"):
            data_processor = self.__get_data_processor(data_processor_id=relay_processor.get("data_processor_id"))
        relay_processor["data_processor"] = data_processor
        return relay_processor

    def __get_data_processor(self, data_processor_id):
        """
        Fetch data processor
        :param data_processor_id:
        :return:
        """
        data_processor = DataProcessor.objects.filter(id=data_processor_id, is_deleted=False).first()
        return DataProcessorSerializer(instance=data_processor, many=False).data

    def add_processor(self, event_id, data):
        """
        Adds a relay and corresponding data processor to the registered event
        :param event_id:
        :param data:
        :return:
        """
        data_processor_id = 0
        relay_processor_data = data.get("relay_processor")
        data_processor_data = data.get("data_processor")
        if data_processor_data:
            data_processor_id = self.__add_data_processor(data=data_processor_data)
        relay_processor_data["data_processor_id"] = data_processor_id
        relay_processor_data["source_event_id"] = event_id
        relay_processor_data["is_active"] = True

        self.__validate_relay_processor(data=relay_processor_data)
        relay_processor = RelayProcessor(**relay_processor_data)
        relay_processor.save()
        return {"message": "Processor added successfully for the event"}

    def __add_data_processor(self, data):
        """
        Saves data processor
        The same data processor can be used for different relay processors if the payload has to be the same
        :param data:
        :return:
        """
        if data.get("id"):
            return data["id"]
        self.__validate_data_processor(data=data)
        data_processor = DataProcessor(**data)
        data_processor.save()
        return data_processor.id

    def __validate_data_processor(self, data):
        """
        Validates data processor
        :param data:
        :return:
        """
        ValidityUtil().is_valid_json_schema(schema=data.get("relay_json_schema"))
        ValidityUtil().is_valid_graphql_query(query=data.get("graphql_query"))

    def __validate_relay_processor(self, data):
        """
        Validates relay processor
        :param data:
        :return:
        """
        if data.get("relay_type") not in RelayType.list():
            raise InvalidInputException("Relay type not supported")
        if data.get("relay_type") == RelayType.API.value:
            ValidityUtil().is_valid_json_logic_rule(rules=data.get("relay_http_endpoint_rules"))
        elif data.get("relay_type") == RelayType.EVENT.value:
            ValidityUtil().is_valid_json_logic_rule(rules=data.get("relay_event_rules"))

    def update_processor(self, event_id, relayer_id, data):
        """
        Updates the relay or data processor for the event
        :param event_id:
        :param relayer_id:
        :param data:
        :return:
        """
        updated_data_processor = {}
        relay_processor = RelayProcessor.objects.filter(id=relayer_id, is_deleted=False).first()
        if not relay_processor:
            raise InvalidInputException("Relay Processor not found")
        relay_processor_data = data.get("relay_processor")
        data_processor_data = data.get("data_processor")
        if data_processor_data:
            updated_data_processor = self.__update_data_processor(data=data_processor_data)
        self.__validate_relay_processor(data=relay_processor_data)
        for key, value in relay_processor_data.items():
            setattr(relay_processor, key, value)
        relay_processor.save()
        updated_relay_processor = RelayProcessorSerializer(instance=relay_processor, many=False).data
        return {"relay_processor": updated_relay_processor, "data_processor": updated_data_processor}

    def __update_data_processor(self, data):
        """
        Updates data processor
        :param data:
        :return:
        """
        data_processor = DataProcessor.objects.filter(id=data.get("id"), is_deleted=False).first()
        if not data_processor:
            raise InvalidInputException("Data Processor not found")
        self.__validate_data_processor(data=data)
        for key, value in data.items():
            setattr(data_processor, key, value)
        data_processor.save()
        return DataProcessorSerializer(instance=data_processor, many=False).data
