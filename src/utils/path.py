import urllib

def no_slash(path):
    if path=="" or path=="/":
        return ""
    if path.startswith("/"):
        path = path[1:]
    if path.endswith("/"):
        path = path[:-1]
    return path

def left_slash(path):
    if path=="" or path=="/":
        return "/"
    if not path.startswith("/"):
        path = "/" + path
    if path.endswith("/"):
        path = path[:-1]
    return path

def right_slash(path):
    if path=="" or path=="/":
        return "/"
    if path.startswith("/"):
        path = path[1:]
    if not path.endswith("/"):
        path = path + "/"
    return path

def both_slash(path):
    if path=="" or path=="/":
        return "/"
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path = path + "/"
    return path

def url_decode(url):
    return urllib.unquote(url).decode('iso-8859-2')