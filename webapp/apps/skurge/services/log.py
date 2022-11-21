from webapp.apps.skurge.models import RelayEventLogs


class RelayLogService:

    def log(self, source, status, destination=None, relay_type=None, relay_data=None, reason=None):
        """
        Logs the skurge event in db
        :return:
        """
        relay_logs_json = {
            "source_event_name": source,
            "destination_relay_name": destination,
            "relay_type": relay_type,
            "relay_data": relay_data,
            "status": status,
            "reason": reason
        }
        relay_log = RelayEventLogs(**relay_logs_json)
        relay_log.save()
