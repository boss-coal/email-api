import os
from datetime import datetime, timedelta
import time

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

def gmTimestampFromAscTime(asctime, fmt='%a, %d %b %Y %H:%M:%S'):
    index = asctime.rindex(':') + 3
    time_str = asctime[:index]
    index += 1
    utc = int(asctime[index:index+3])
    local = datetime.strptime(time_str, fmt)
    gm_time =  local - timedelta(hours=utc)
    return int(time.mktime(gm_time.timetuple()))

def gmTimestapFromIsoDate(s, time_zone=8, fmt='%Y-%m-%d'):
    return int(time.mktime(time.strptime(s, fmt))) - time_zone*3600