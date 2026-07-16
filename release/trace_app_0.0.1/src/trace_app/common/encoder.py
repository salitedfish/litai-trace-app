import json
from datetime import datetime, date
from decimal import Decimal

from bson import ObjectId


class DefaultEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %X')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, Decimal):
            return int(o)
        else:
            return super().default(o)
