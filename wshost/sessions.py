import random
import string


sessions = {}

def new_session(name, id_length=32):
    id = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(id_length))
    sessions[id] = name
    return id

def get_session(id):
    if id not in sessions:
        return False
    
    return sessions[id]

def remove_session(id):
    sessions.pop(id)
