from datetime import datetime
from datetime import timezone
from wshost import headers
from hashlib import md5
import os


def generate_etag(content):
    return f'"{md5(content).hexdigest()}"'

def check_etag(request, etag):
    if "If-None-Match" in request["header"]:
        return request["header"]["If-None-Match"] == etag
      
    return False

def get_last_modified(path):
    last_modified = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
    return headers.encode_time(last_modified.timetuple())
