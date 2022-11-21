from unittest.mock import patch
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from webapp.apps.skurge.tests.common.util import add_sample_data, mocked_get_data_from_graphql, \
    mocked_publish, update_relay_processor, update_data_processor
from webapp.apps.skurge.constants import RelayType


class ProcessEventTest(APITestCase):

    @patch('webapp.apps.skurge.clients.event.RabbitMQClient.publish', mocked_publish)
    @patch('webapp.apps.skurge.common.util.HttpUtil.publish_message', mocked_publish)
    @patch('webapp.apps.skurge.clients.graphql.GraphQLClient.fetch_data', mocked_get_data_from_graphql)
    def test_process_event_relay_type_event(self):
        """
            Test processing & relaying of source event with relay event type "EVENT"
        """
        source_event = add_sample_data(RelayType.EVENT)[0]
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'SUCCESS')

    @patch('webapp.apps.skurge.clients.event.RabbitMQClient.publish', mocked_publish)
    @patch('webapp.apps.skurge.common.util.HttpUtil.publish_message', mocked_publish)
    @patch('webapp.apps.skurge.clients.graphql.GraphQLClient.fetch_data', mocked_get_data_from_graphql)
    def test_process_event_relay_type_api(self):
        """
            Test processing & relaying of source event with relay event type "API"
        """
        source_event = add_sample_data(RelayType.API)[0]
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'SUCCESS')

    def test_process_unregistered_event(self):
        """
            Test processing & relaying of unregistered source event.
        """
        add_sample_data()
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': 'RANDOM_EVENT'}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'FAILED')

    def test_process_event_with_invalid_payload(self):
        """
            Test processing & relaying of source event with invalid api payload.
        """
        source_event = add_sample_data()[0]
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'FAILED')

    def test_process_event_with_no_relay_processor(self):
        """
            Test processing & relaying of source event with no relay processor.
        """
        sample_data = add_sample_data()
        source_event = sample_data[0]
        relay_processor = sample_data[2]
        update_relay_processor(relay_processor['id'], {'is_active': False})  # mark relay processor as inactive
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'FAILED')

    @patch('webapp.apps.skurge.clients.graphql.GraphQLClient.fetch_data', mocked_get_data_from_graphql)
    def test_process_event_with_no_relay_event_rules(self):
        """
            Test processing & relaying of source event with no relay event rules.
        """
        sample_data = add_sample_data()
        source_event = sample_data[0]
        relay_processor = sample_data[2]
        update_relay_processor(relay_processor['id'], {'relay_event_rules': None})
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'SUCCESS')

    @patch('webapp.apps.skurge.clients.graphql.GraphQLClient.fetch_data', mocked_get_data_from_graphql)
    def test_process_event_with_no_valid_relay_event(self):
        """
            Test processing & relaying of source event with no valid relay event.
            No communication will hence be delivered.
        """
        sample_data = add_sample_data()
        source_event = sample_data[0]
        relay_processor = sample_data[2]
        update_relay_processor(relay_processor['id'], {'relay_event_rules': {"if": [{"==": [1, 2]}, "SEND_EMAIL"]}})
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'SUCCESS')

    @patch('webapp.apps.skurge.clients.graphql.GraphQLClient.fetch_data', mocked_get_data_from_graphql)
    def test_process_event_with_no_conditions_matching_in_relay_data_locator(self):
        """
            Test processing & relaying of source event with no condition matching in relay_data_locator.
            No communication will hence be delivered.
        """
        sample_data = add_sample_data()
        source_event = sample_data[0]
        data_processor = sample_data[1]
        update_data_processor(data_processor['id'], {'relay_data_locator': {"if": [{"==": [1, 2]}, {"template_id": "email-template-for-india", "template_data.name": "userDetails.name"}]}})
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'SUCCESS')

    @patch('webapp.apps.skurge.clients.graphql.GraphQLClient.fetch_data', mocked_get_data_from_graphql)
    def test_process_event_with_invalid_relay_data(self):
        """
            Test processing & relaying of source event with relay data not satisfying relay_json_schema.
            No communication will hence be delivered.
        """
        sample_data = add_sample_data()
        source_event = sample_data[0]
        data_processor = sample_data[1]
        update_data_processor(data_processor['id'], {'relay_json_schema': {"type": "object", "required": ["new_field"], "properties": {"new_field": {"type": "string"}}}})
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'SUCCESS')

    @patch('webapp.apps.skurge.clients.graphql.GraphQLClient.fetch_data', mocked_get_data_from_graphql)
    def test_process_event_with_no_valid_api_http_params(self):
        """
            Test processing & relaying of source event with no valid API HTTP parameters.
            No communication will hence be delivered.
        """
        sample_data = add_sample_data(RelayType.API)
        source_event = sample_data[0]
        relay_processor = sample_data[2]
        update_relay_processor(relay_processor['id'], {'relay_http_endpoint_rules': {"if": [{"==": [{"var": "country_code"}, "IN"]}, {"headers": {"Content-Type": "application/json"}, "http_endpoint": "https://api.abc.com/pqr"}]}})
        response = self.client.post(path=reverse(viewname='skurge-relayer', kwargs={'event_name': source_event['source_event']}),
                                    data={'user_id': 1234}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['response']['status'], 'SUCCESS')
