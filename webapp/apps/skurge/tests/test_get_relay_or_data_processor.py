from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.util import add_sample_data, compare_relay_processors, compare_data_processors


class GetRelayAndDataProcessorTest(APITestCase):

    def setUp(self):
        self.source_event, self.data_processor, self.relay_processor = add_sample_data()

    def test_get_relay_and_data_processor(self):
        """
            Test getting data and relay processor with given event_id and relayer_id.
        """
        response = self.client.get(path=reverse(viewname='update-relay-processor',
                                                kwargs={'event_id': self.source_event['id'], 'relayer_id': self.relay_processor['id']}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(compare_relay_processors(response.data["response"], self.relay_processor))
        self.assertTrue(compare_data_processors(response.data["response"]["data_processor"], self.data_processor))
