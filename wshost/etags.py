from wshost import responses
from wshost import headers
from wshost import statuses
import datetime
import hashlib
import os


def generate_etag(content):
    return f'"{hashlib.md5(content).hexdigest()}"'

def check_etag(request, etag):
    if "If-None-Match" in request["header"]:
        if request["header"]["If-None-Match"] == etag:
            return True
              
    return False

def get_last_modified(path):
    return headers.encode_time(datetime.datetime.utcfromtimestamp(os.path.getmtime(path)).timetuple())

def not_modified(content, last_modified):
    return responses.Response(content, status=statuses.NOT_MODIFIED, header=[("Last-Modified", last_modified)], etag=True, no_content=False)
