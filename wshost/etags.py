from wshost import headers
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
