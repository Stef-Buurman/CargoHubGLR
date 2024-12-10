from datetime import datetime


class Base:
    def __init__(): # pragma: no cover
        pass

    def get_timestamp(self): # pragma: no cover
        return datetime.utcnow().isoformat() + "Z"
