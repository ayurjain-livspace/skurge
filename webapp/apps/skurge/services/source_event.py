import logging

from webapp.apps.skurge.models import SourceEvent
from webapp.apps.skurge.serializers.source_event import SourceEventSerializer
from webapp.apps.skurge.common.util import ValidityUtil
from webapp.apps.skurge.common.exceptions import InvalidInputException
from webapp.apps.skurge.services.relay_event import RelayEventService


class SourceEventService:

    def get_all_registered_events(self):
        """
        Fetches all events registered in skurge
        :return:
        """
        registered_events = SourceEvent.objects.filter(is_active=True, is_deleted=False).all()
        return SourceEventSerializer(instance=registered_events, many=True).data

    def register_event(self, data):
        """
        Registers an event in skurge
        :param data:
        :return:
        """
        self.__validate_input(data=data)
        source_event = SourceEvent(**data)
        source_event.save()
        return SourceEventSerializer(instance=source_event, many=False).data

    def get_registered_event(self, event_id):
        """
        Gets registered event along with its processors
        :param event_id:
        :return:
        """
        source_event = SourceEvent.objects.filter(id=event_id, is_deleted=False, is_active=True).first()
        event_json = SourceEventSerializer(instance=source_event, many=False).data
        processors = RelayEventService().get_processors_for_event(event_id=event_id)
        event_json["processors"] = processors
        return event_json

    def __validate_input(self, data):
        """
        Validates the incoming data
        :param data:
        :return:
        """
        if not data.get("source_event"):
            raise InvalidInputException("Source event not specified")
        if "is_active" not in data.keys():
            data["is_active"] = True
        ValidityUtil().is_valid_json_schema(schema=data.get("input_json_schema"))
        logging.info("Validation successful")

    def update_event(self, event_id, data):
        """
        Updates an existing event registered in skurge
        :param event_id:
        :param data:
        :return:
        """
        source_event = SourceEvent.objects.filter(id=event_id, is_deleted=False).first()
        if not source_event:
            raise InvalidInputException("Event not registered in skurge")
        self.__validate_input(data=data)
        for key, value in data.items():
            setattr(source_event, key, value)
        source_event.save()
        return SourceEventSerializer(instance=source_event, many=False).data
