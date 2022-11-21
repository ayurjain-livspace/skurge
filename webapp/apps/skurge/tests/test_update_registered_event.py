from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.util import add_sample_source_event, compare_source_events


class UpdateSourceEventTest(APITestCase):

    def setUp(self):
        self.source_event = add_sample_source_event()

    def test_update_source_event(self):
        """
            Test updating a registered source event.
        """
        self.source_event['source_event'] = 'NEW_TEST_EVENT'
        response = self.client.put(path=reverse(viewname='get-update-registered-event', kwargs={'event_id': self.source_event['id']}),
                                   data=self.source_event, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(compare_source_events(response.data["response"], self.source_event))
