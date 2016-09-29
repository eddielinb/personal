import sqlite3
from random import randint
import time


conn = sqlite3.connect('webui.db')

query_sensor = 'INSERT INTO SENSOR (ID, MAC) VALUES'
for mac in range(1,501):
    temp = "(" + str(mac) + ",'" + format(mac, "016d") + "'),"
    query_sensor += temp

conn.execute(query_sensor[:-1])
conn.commit()

query_request = 'INSERT INTO REQUEST (ID, MAC, TIMESTAMP) VALUES'

ts_start = int(time.time()) - 3600 * 24
ts_end = ts_start + 3600 * 24
print ts_start
print ts_end

for mac in range(1,501):
    for count in range(1, 241):
        timestamp_ran = randint(1, 3600*24) + ts_start
        temp = "(" + str((mac-1) * 240 + count) + ",'" + format(mac, "016d") + "'," + str(timestamp_ran) + "),"
        query_request += temp
conn.execute(query_request[:-1])
conn.commit()

conn.close()