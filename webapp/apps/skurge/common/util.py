from rest_framework import status
from rest_framework.response import Response
from jsonschema import Draft7Validator
from json_logic import jsonLogic, is_logic
from webapp.apps.skurge.clients.http import HttpClient
from webapp.apps.skurge.common.exceptions import InvalidInputException


class HttpUtil:

    def publish_message(self, url, http_method, data, headers):
        """
        Runs the api of the corresponding http_method with the given headers
        :param url:
        :param http_method:
        :param data:
        :param headers:
        :return:
        """
        http_client = HttpClient()
        method = getattr(http_client, http_method)
        response = method(url=url, headers=headers, data=data if data else {})
        return response


class ValidityUtil:

    def is_valid_json_schema(self, schema):
        """
        Checks if the provided schema is a valid json schema or not
        :param schema:
        :return:
        """
        Draft7Validator.check_schema(schema)

    def is_valid_json_logic_rule(self, rules):
        """
        Checks if the given rule json object is valid according to jsonLogic
        :param rules:
        :return:
        """
        if not is_logic(rules):
            raise InvalidInputException("Not a valid jsonLogic rule")
        jsonLogic(rules, {})

    def is_valid_graphql_query(self, query):
        """
        Checks if the given query is a valid graphql query
        :param query:
        :return:
        """
        return True


class APIResponse:

    @staticmethod
    def send(data, code=status.HTTP_200_OK, error=""):
        """Overrides rest_framework response

            :param data: data to be send in response
            :param code: response status code(default has been set to 200)
            :param error: error message(if any, not compulsory)
        """
        res = {"error": error, "response": data}
        return Response(data=res, status=code)
