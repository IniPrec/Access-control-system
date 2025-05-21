import random
import string

def generate_rfid():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))