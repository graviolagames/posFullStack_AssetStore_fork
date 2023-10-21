import hashlib

def create_hash(input_string):
    hash = hashlib.md5(input_string.encode()).hexdigest()
    print("Hash for "+input_string+ " : "+hash)
    return hash