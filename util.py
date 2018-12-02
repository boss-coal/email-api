import os
def toRemoteOrDbFormat(src, map, from_to):
    des = {}
    for item in map:
        des[item[from_to[1]]] = src.get(item[from_to[0]], item[2])
    return des


def fileHash(path):
    f = open(path, 'rb')
    result = hash(f.read())
    f.close()
    return result

def getLocalFilePath(local_path):
    dirname, filename = os.path.split(os.path.abspath(__file__))
    return os.path.join(dirname, local_path)
