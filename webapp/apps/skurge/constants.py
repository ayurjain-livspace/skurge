from enum import Enum


class RelayType(Enum):
    API = "API"
    EVENT = "EVENT"

    @staticmethod
    def list():
        return list(map(lambda rt: rt.value, RelayType))
