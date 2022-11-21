from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.util import add_sample_data, compare_data_processors, compare_relay_processors


class UpdateRelayAndDataProcessorTest(APITestCase):

    def setUp(self):
        self.source_event, self.data_processor, self.relay_processor = add_sample_data()

    def test_update_relay_and_data_processor(self):
        """
            Test updating relay and data processor of a registered source event.
        """
        self.data_processor['default_response']['new_default_key'] = 'new_default_value'
        self.relay_processor['relay_system'] = 'new_relay_system'
        response = self.client.put(path=reverse(viewname='update-relay-processor',
                                                kwargs={'event_id': self.source_event['id'], 'relayer_id': self.relay_processor['id']}),
                                   data={"data_processor": self.data_processor, "relay_processor": self.relay_processor}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(compare_data_processors(response.data['response']['data_processor'], self.data_processor))
        self.assertTrue(compare_relay_processors(response.data['response']['relay_processor'], self.relay_processor))
