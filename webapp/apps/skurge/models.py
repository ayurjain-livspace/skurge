from simple_history.models import HistoricalRecords
from django.db import models
from django.contrib.postgres.fields import JSONField


class BaseModel(models.Model):
    """
        This is an abstract model class to add is_deleted, created_at and modified at fields in any model
    """
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """ Soft delete """
        self.is_deleted = True
        self.save()


class RelayEventLogs(BaseModel):
    """
    Logs the skurge event
    Right now logging only the failed events
    """
    source_event_name = models.CharField(max_length=100, null=False)
    destination_relay_name = models.CharField(max_length=512, null=True)
    relay_type = models.CharField(max_length=20, null=True)
    relay_data = JSONField(null=True)
    status = models.CharField(max_length=20, null=False)
    reason = models.CharField(max_length=256, null=True)

    class Meta:
        db_table = "relay_logs"


class SourceEvent(BaseModel):
    """
    All events registered on skurge are present in this table
    Also used for validating the input data coming to skurge
    """
    source_event = models.CharField(null=False, max_length=128)
    is_active = models.BooleanField(default=True)
    input_json_schema = JSONField()

    source_event_history = HistoricalRecords(excluded_fields=['is_active'])

    class Meta:
        db_table = "source_events"


class DataProcessor(BaseModel):
    """
    data_processor table to create the corresponding relay data to be sent to all the relayers
    uses graphql query to fetch data from external clients which this sent to all the destinations
    """
    graphql_query = models.TextField()
    relay_data_locator = JSONField()
    default_response = JSONField(null=True)
    relay_json_schema = JSONField()

    data_processor_history = HistoricalRecords(excluded_fields=['is_active'])

    class Meta:
        db_table = "data_processors"


class RelayProcessor(BaseModel):
    """
    relay_processor table to identify the destination where to send the relay data
    Can be either sent to some api/event to any onboarded system
    """
    source_event_id = models.IntegerField(null=False, default=0)
    is_active = models.BooleanField(default=True)
    relay_type = models.CharField(null=False, max_length=20)
    relay_system = models.CharField(null=False, max_length=128)
    relay_event_rules = JSONField(null=True)
    context_data_locator = JSONField(null=True)
    relay_http_endpoint_rules = JSONField(null=True)
    data_processor_id = models.IntegerField(null=True)

    relay_processor_history = HistoricalRecords(excluded_fields=['is_active'])

    class Meta:
        db_table = "relay_processors"
