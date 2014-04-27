import math

def convert_data_size(size):
    if size >= math.pow(10,12):
        return str(round(size / math.pow(10,12), 2)) + " TB";
    elif size >= math.pow(10,9):
        return str(round(size / math.pow(10,9), 2)) + " GB";
    elif size >= math.pow(10,6):
        return str(round(size / math.pow(10,6), 2)) + " MB";
    elif size >= math.pow(10,3):
        return str(round(size / math.pow(10,3), 2)) + " KB";
    else:
        return str(size) + " B";
