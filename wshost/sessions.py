import random
import string


sessions = {}

def new_session(value, id_length=32):
    id = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(id_length))
    sessions[id] = value
    return id

def get_session(id): 
    return sessions[id]

def check_session(id):
    return id in sessions

def set_session(id, value):
    sessions[id] = value

def remove_session(id):
    sessions.pop(id)
