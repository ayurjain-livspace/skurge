import logging
import copy
from django.conf import settings
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from webapp.apps.skurge.common.exceptions import InvalidInputException


class GraphQLClient:
    """
    Base class for a graphql server.
    Can connect to any graphql server to fetch data
    """
    graphql_endpoint = None
    headers = None
    secure = None

    def __init__(self, extra_headers=None):
        service_conf = copy.deepcopy(settings.EXTERNAL_SERVICES.get("GRAPHQL_SERVER", {}))
        gateway_conf = copy.deepcopy(settings.GATEWAY)
        if service_conf.get("GATEWAY", {}).get("ENABLED"):
            if not gateway_conf or not service_conf.get("GATEWAY", {}).get("PATH"):
                raise InvalidInputException("Gateway is enabled but config not found")
            self.graphql_endpoint = gateway_conf.get("HOST") + service_conf.get("GATEWAY").get("PATH")
            self.headers = gateway_conf.get("HEADERS")
        else:
            self.graphql_endpoint = service_conf.get("HOST")
            self.headers = service_conf.get("HEADERS")

        if extra_headers:
            for key, value in extra_headers.items():
                self.headers[key] = value

    def get_baseurl(self):
        protocol = "https://" if self.secure else "http://"
        return protocol + self.graphql_endpoint

    def get_headers(self):
        return self.headers

    def fetch_data(self, query, variables):
        """
        Fetches data from the given graphql server
        :return:
        """
        url = self.get_baseurl()
        headers = self.get_headers()
        logging.info("Fetching data for query %s and variables %s from %s graphql server", query, variables, url)
        transport = RequestsHTTPTransport(url=url, use_json=True, headers=headers)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql(query)
        response = client.execute(query, variable_values=variables)
        logging.info("Response from graphql server: %s", response)
        return response
