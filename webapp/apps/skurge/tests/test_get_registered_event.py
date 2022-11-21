from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.util import add_sample_data, add_sample_relay_processor, compare_source_events, \
    compare_data_processors, compare_relay_processors
from webapp.apps.skurge.constants import RelayType


class GetSourceEventTest(APITestCase):

    def setUp(self):
        self.source_event, self.data_processor, self.relay_processor_relay_type_event = add_sample_data(relay_type=RelayType.EVENT)
        self.relay_processor_relay_type_api = add_sample_relay_processor(source_event_id=self.source_event['id'], data_processor_id=self.data_processor['id'], relay_type=RelayType.API)

    def test_get_source_event(self):
        """
            Test getting source event with given event_id.
        """
        response = self.client.get(path=reverse(viewname='get-update-registered-event', kwargs={'event_id': self.source_event['id']}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(compare_source_events(response.data['response'], self.source_event))
        processors = response.data['response']['processors']
        self.assertEqual(len(processors), 2)
        for processor in processors:
            self.assertTrue(compare_data_processors(processor.get('data_processor'), self.data_processor))
            if processor.get('relay_type') == RelayType.EVENT.value:
                self.assertTrue(compare_relay_processors(processor, self.relay_processor_relay_type_event, relay_type=RelayType.EVENT))
            else:
                self.assertTrue(compare_relay_processors(processor, self.relay_processor_relay_type_api, relay_type=RelayType.API))
