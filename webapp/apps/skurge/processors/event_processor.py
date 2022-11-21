import logging

from webapp.apps.skurge.processors.source_event import SourceEventProcessor
from webapp.apps.skurge.processors.relay_event import RelayEventProcessor
from webapp.apps.skurge.services.log import RelayLogService


class EventProcessor:
    """
    Processor class to process any incoming skurge event
    """
    source_event_name = None
    source_data = None
    relay_processors = None

    def __init__(self, source_event, source_data):
        self.source_event_name = source_event
        self.source_data = source_data

    def process_event(self):
        """
        Processes the incoming skurge event to relay it to different systems
        :return:
        """
        error_message = self.validate_source_event()
        if error_message:
            return {"status": "FAILED", "reason": error_message}
        self.relay_event()
        return {"status": "SUCCESS"}

    def validate_source_event(self):
        """
        Validates incoming event to skurge
        :return:
        """
        source_event_processor = SourceEventProcessor(self.source_event_name, self.source_data)
        if not source_event_processor.is_source_event_registered():
            message = "Event %s is not registered within skurge or is marked inactive" % self.source_event_name
            logging.warning(message)
            RelayLogService().log(source=self.source_event_name, status="FAILED", reason=message)
            return message
        error_messages = source_event_processor.validate_source_data()
        if error_messages:
            messages = ','.join(error_messages)
            RelayLogService().log(source=self.source_event_name, status="FAILED", reason=messages)
            return messages
        source_event_id = source_event_processor.source_event_id
        self.relay_processors = RelayEventProcessor().fetch_relay_processors(source_event_id=source_event_id)
        if not self.relay_processors:
            message = "No relay event processor registered for the source event %s" % self.source_event_name
            logging.warning(message)
            RelayLogService().log(source=self.source_event_name, status="FAILED", reason=message)
            return message
        return None

    def relay_event(self):
        """
        Iterates the list of relayers for the source event, prepares the payload and relays it forward.
        Logs error for any failed relay_processor.
        :return:
        """
        for relay_processor in self.relay_processors:
            try:
                RelayEventProcessor().process_relayer(relay_processor=relay_processor, source_data=self.source_data,
                                                      source_event=self.source_event_name)
            except Exception as e:
                err = "Error processing relayer: %s, source event: %s, Error: %s" % (relay_processor.get("id"), self.source_event_name, str(e))
                logging.error(err)
