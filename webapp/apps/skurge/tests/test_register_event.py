import copy
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.constants import TestData
from webapp.apps.skurge.tests.common.util import compare_source_events


class RegisterSourceEventTest(APITestCase):

    def setUp(self):
        self.source_event = TestData.get_source_event()

    def test_register_source_event(self):
        """
            Test registering a new source event with valid payload.
        """
        response = self.client.post(path=reverse('register-event'), data=self.source_event, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(compare_source_events(response.data["response"], self.source_event))

    def test_register_invalid_source_event(self):
        """
            Test registering a new source event with invalid payload.
            This will show exception in logs.
        """
        invalid_source_event = copy.deepcopy(self.source_event)
        invalid_source_event.pop('source_event')
        response = self.client.post(path=reverse('register-event'), data=invalid_source_event, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
