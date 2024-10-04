import random
import string
import time


sessions = {}

def new_session(value, id_length=32, expire=90*24*60):
    id = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(id_length))
    sessions[id] = {"value":value, "expire": time.time + expire}
    return id

def get_session(id): 
    if id not in sessions:
        return None

    if sessions[id]["expire"] >= time.time():
        remove_session(id)
        return None
    
    return sessions[id]["value"]

def set_session(id, value):
    sessions[id]["value"] = value

def remove_session(id):
    sessions.pop(id)
