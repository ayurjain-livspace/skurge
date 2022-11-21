import logging

from rest_framework.views import APIView

from webapp.apps.skurge.common.util import APIResponse
from webapp.apps.skurge.processors.event_processor import EventProcessor
from webapp.apps.skurge.services.source_event import SourceEventService
from webapp.apps.skurge.services.relay_event import RelayEventService


class EventProcessorView(APIView):

    def post(self, request, event_name=None):
        """
        Processes incoming events and relays it forward to multiple systems
        :param request:
        :param event_name:
        :return:
        """
        logging.info("Received request for event %s to be processed by skurge v1 with data %s", event_name, request.data)
        base_processor = EventProcessor(source_event=event_name, source_data=request.data)
        response = base_processor.process_event()
        logging.info("Event processed by skurge successfully")
        return APIResponse.send(response)


class RegisteredEventsView(APIView):

    def get(self, request):
        """
        Gets all events registered in skurge
        :param request:
        :return:
        """
        logging.info("Request received to fetch all register events")
        response = SourceEventService().get_all_registered_events()
        logging.info("Fetch registered event response %s", response)
        return APIResponse.send(response)


class SourceEventView(APIView):

    def post(self, request):
        """
        Registers an event in source_events, Only these events will be processed by skurge
        :param request:
        :return:
        """
        logging.info("Request received to register event with data %s", request.data)
        response = SourceEventService().register_event(data=request.data)
        logging.info("Registered event response %s", response)
        return APIResponse.send(response)

    def get(self, request, event_id):
        """
        Gets an event and all its processors
        :param request:
        :param event_id:
        :return:
        """
        logging.info("Request received to get register event %s", event_id)
        response = SourceEventService().get_registered_event(event_id=event_id)
        logging.info("Get event response %s", response)
        return APIResponse.send(response)

    def put(self, request, event_id):
        """
        Updates an event registered in skurge
        :param request:
        :param event_id:
        :return:
        """
        logging.info("Request received to update register event %s", event_id)
        response = SourceEventService().update_event(event_id=event_id, data=request.data)
        logging.info("Updated event response %s", response)
        return APIResponse.send(response)


class RelayEventView(APIView):

    def post(self, request, event_id):
        """
        Add relay and data processor to the registered event
        :param request:
        :param event_id:
        :return:
        """
        logging.info("Request received to add relay and data processor for register event %s", event_id)
        response = RelayEventService().add_processor(event_id=event_id, data=request.data)
        logging.info("Added relay processor response %s", response)
        return APIResponse.send(response)

    def put(self, request, event_id, relayer_id):
        """
        Updates relay or data processor to the registered event
        :param request:
        :param event_id:
        :param relayer_id:
        :return:
        """
        logging.info("Request received to update relay processor %s for register event %s", relayer_id, event_id)
        response = RelayEventService().update_processor(event_id=event_id, relayer_id=relayer_id, data=request.data)
        logging.info("Update relay processor response %s", response)
        return APIResponse.send(response)

    def get(self, request, event_id, relayer_id):
        """
        Gets relay or data processor to the registered event
        :param request:
        :param event_id:
        :param relayer_id:
        :return:
        """
        logging.info("Request received to get relay processor %s for register event %s", relayer_id, event_id)
        response = RelayEventService().get_relay_processor(event_id=event_id, relay_processor_id=relayer_id)
        logging.info("get relay processor response %s", response)
        return APIResponse.send(response)
