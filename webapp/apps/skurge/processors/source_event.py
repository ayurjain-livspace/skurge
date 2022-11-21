import logging
import jsonschema

from webapp.apps.skurge.models import SourceEvent


class SourceEventProcessor:
    source_event_id = None
    source_event = None
    source_data = None
    input_schema = None

    def __init__(self, source_event, source_data):
        self.source_event = source_event
        self.source_data = source_data

    def is_source_event_registered(self):
        """
        Checks if source event is registered in skurge
        :return:
        """
        registered_event = SourceEvent.objects.filter(source_event=self.source_event, is_active=True,
                                                      is_deleted=False).first()
        if not registered_event:
            return False
        self.source_event_id = registered_event.id
        self.input_schema = registered_event.input_json_schema
        return True

    def validate_source_data(self):
        """
        Validates in the source data using the validator object
        :return:
        """
        validator = jsonschema.Draft7Validator(self.input_schema)
        errors = validator.iter_errors(self.source_data)
        error_info = []
        for error in errors:
            if hasattr(error, "message"):
                error_info.append(error.message)
        if error_info:
            logging.warning("Request Validation Failed. %s", error_info)
            return error_info
        logging.info("Source data validated.")
        return None
