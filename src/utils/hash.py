import hashlib

def hash_file(fpath, hasher=hashlib.sha256(), blocksize=65536):
    f = open(fpath, 'rb')
    buf = f.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = f.read(blocksize)
    return hasher.hexdigest()

def hash_dir(dname, item_hashs, hasher=hashlib.sha256()):
    hasher.update(dname)
    for item_hash in item_hashs:
        hasher.update(item_hash)
    return hasher.hexdigest()