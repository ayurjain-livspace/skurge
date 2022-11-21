import logging
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from django.conf import settings


class HttpClient:
    """
    HttpClient implementation for python projects.
    """

    def __init__(self, timeout=60):
        """
        :param timeout: Timeout in seconds

        The following params can be specified in settings as HTTP:
        :backoff: Backoff factor for the exponential backoff
        :status_forcelist: A list of statuses on which to retry the HTTP(S) calls
        """
        self.__timeout = timeout

        # Create the session
        self.__session = requests.Session()

        # Setup the retries object
        try:
            max_retries = settings.HTTP.get("max_retries")
        except:
            # Default max_retries to 5
            max_retries = 5

        try:
            backoff = settings.HTTP.get("backoff")
        except:
            # Default backoff_factor of Retry to 0.1
            backoff = 0.1

        try:
            status_forcelist = settings.HTTP.get("status_forcelist")
        except:
            # Default status_checklist to 501...503
            status_forcelist = [500, 501, 502, 503]

        retries = Retry(total=max_retries, backoff_factor=backoff,
                        status_forcelist=status_forcelist)

        # Ensure all http and https called made via the session are retried
        self.__session.mount('http://', HTTPAdapter(max_retries=retries))
        self.__session.mount('https://', HTTPAdapter(max_retries=retries))

    def set_timeout(self, timeout):
        self.__timeout = timeout
        return self

    def get(self, **kwargs):
        """Sends a GET request.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        logging.info(
            "GET URL: {url}, HEADERS: {headers}".format(url=kwargs.get("url", ""), headers=kwargs.get("headers", "")))
        kwargs["timeout"] = self.__timeout
        r = self.__session.get(**kwargs)
        r.raise_for_status()
        return r

    def delete(self, **kwargs):
        """Sends a DELETE request.
        :param url: URL for the new :class:`Request` object.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        logging.info("DELETE URL: {url}, HEADERS: {headers}".format(url=kwargs.get("url", ""),
                                                                    headers=kwargs.get("headers", "")))
        kwargs["timeout"] = self.__timeout
        r = self.__session.delete(**kwargs)
        r.raise_for_status()
        return r

    def post(self, **kwargs):
        """Sends a POST request.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) json data to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        logging.info(
            "POST URL: {url}, HEADERS: {headers}".format(url=kwargs.get("url", ""), headers=kwargs.get("headers", "")))
        kwargs["timeout"] = self.__timeout
        r = self.__session.post(**kwargs)
        r.raise_for_status()
        return r

    def put(self, **kwargs):
        """Sends a PUT request.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        logging.info(
            "PUT URL: {url}, HEADERS: {headers}".format(url=kwargs.get("url", ""), headers=kwargs.get("headers", "")))
        kwargs["timeout"] = self.__timeout
        r = self.__session.put(**kwargs)
        r.raise_for_status()
        return r

    def patch(self, **kwargs):
        """Sends a PATCH request.
        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param kwargs: Optional arguments that ``request`` takes.
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """

        logging.info(
            "PATCH URL: {url}, HEADERS: {headers}".format(url=kwargs.get("url", ""), headers=kwargs.get("headers", "")))
        kwargs["timeout"] = self.__timeout
        r = self.__session.patch(**kwargs)
        r.raise_for_status()
        return r
