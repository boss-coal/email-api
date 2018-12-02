import os
from conf import config
from db.fields import table_list, fields
from util import fileHash
import sqlite3
import platform

dirname, filename = os.path.split(os.path.abspath(__file__))

def createDb():
    file_path = os.path.join(dirname, 'db', config.db_name)
    if os.path.isfile(file_path):
        h = fileHash(file_path)
        new_file = os.path.join(dirname, 'db', '%s.%s' % (config.db_name, h))
        if os.path.isfile(new_file):
            os.remove(new_file)
        os.rename(file_path, new_file)
    f = open(file_path, 'wb')
    f.close()

    conn = sqlite3.connect(file_path)
    cur = conn.cursor()
    base_sql = 'create table %s (%s);'
    for table in table_list:
        field = fields[table]
        sql = base_sql % (table, ', '.join(['"%s" %s' % item for item in field]))
        print sql
        cur.execute(sql)
        conn.commit()
    conn.close()



def main():
    try:
        # install "twisted", reference to https://github.com/twisted/twisted/blob/trunk/INSTALL.rst
        import twisted
        system = platform.system()
        if system == 'Windows':
            # for windows, install pywin32
            import win32com
            import win32api
    except Exception, e:
        print 'install failed: %s' % e
        return
    createDb()
    print 'install successfully'


if __name__ == '__main__':
    main()
