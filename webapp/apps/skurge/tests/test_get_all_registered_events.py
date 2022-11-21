from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.util import add_sample_source_event, compare_source_events


class GetAllSourceEventsTest(APITestCase):

    def setUp(self):
        self.source_event = add_sample_source_event()

    def test_get_all_source_events(self):
        """
            Test getting all registered source events in skurge.
        """
        response = self.client.get(path=reverse(viewname='get-all-registered-event'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['response']), 1)
        self.assertTrue(compare_source_events(response.data['response'][0], self.source_event))
