import logging
import json
import pika
from django.conf import settings


class RabbitMQClient:
    """
        RabbitMQ client to publish events to rabbitmq.
    """
    def __init__(self):
        self.config = settings.EXTERNAL_SERVICES.get("EVENT_SERVICE")

    def publish(self, routing_key, data):
        """
        Publishes data to rabbitmq with given routing_key
        @param routing_key:
        @param data:
        """
        logging.info("Publishing event - %s - %s", routing_key, data)
        connection = self._connect()
        channel = connection.channel()
        channel.basic_publish(exchange=self.config['exchange'], routing_key=routing_key, body=json.dumps(data))
        connection.close()
        logging.info("Event has been published")

    def _connect(self):
        """
        Connects to rabbitmq and returns connection object
        @return:
        """
        params = pika.URLParameters(self.config.get('url'))
        return pika.BlockingConnection(params)
