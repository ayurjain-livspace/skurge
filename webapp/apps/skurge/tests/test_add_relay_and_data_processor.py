import copy
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.constants import TestData
from webapp.apps.skurge.tests.common.util import add_sample_source_event


class AddRelayAndDataProcessorTest(APITestCase):

    def setUp(self):
        self.source_event = add_sample_source_event()
        self.data_processor = TestData.get_data_processor()
        self.relay_processor = TestData.get_relay_processor()

    def test_add_relay_and_data_processor(self):
        """
            Test adding relay & data processor to a registered source event with valid payload.
        """
        response = self.client.post(path=reverse(viewname='add-relay-processor', kwargs={'event_id': self.source_event['id']}),
                                    data={"data_processor": self.data_processor, "relay_processor": self.relay_processor}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_invalid_relay_and_data_processor(self):
        """
            Test adding relay & data processor to a registered source event with invalid payload.
            This will show exception in logs.
        """
        invalid_relay_processor = copy.deepcopy(self.relay_processor)
        invalid_relay_processor['relay_type'] = 'INVALID_EVENT_TYPE'
        response = self.client.post(path=reverse(viewname='add-relay-processor', kwargs={'event_id': self.source_event['id']}),
                                    data={"data_processor": self.data_processor, "relay_processor": invalid_relay_processor}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
