import sqlite3
import os


a = [1,2,3,4]
b = 5
if b not in a:
    a.append(b)
    print a
#
# cdir = os.path.abspath(os.path.dirname(__file__))
# conn = sqlite3.connect(os.path.join(cdir, '../database/webui.db'))
#
# # query_data = conn.execute("SELECT * FROM REQUEST WHERE TIMESTAMP >"
# #                           + str(1474815928) + " AND TIMESTAMP <" + str(1474815928+3600) + ";")
# hour_ts = 1474815928
# query_data = conn.execute("SELECT * FROM REQUEST WHERE TIMESTAMP > %s AND TIMESTAMP < %s;"
#                           % (str(hour_ts), str(hour_ts + 3600)))
# #query_data = conn.execute("SELECT * FROM REQUEST WHERE TIMESTAMP > %s AND TIMESTAMP < %s;"
# #                          % (str(1474815928), str(1474815928 + 3600)))
# print type(query_data)
# for row in query_data:
#     print row[2]
#     print row
# print len(query_data.fetchall())
#
# hour_ts_start = 1474815928
# for hour_ts in range(0, 3600 * 24, 3600):
#     query_data = conn.execute("SELECT * FROM REQUEST WHERE TIMESTAMP > %s AND TIMESTAMP < %s;"
#                               % (str(hour_ts + hour_ts_start), str(hour_ts + 3600 + hour_ts_start)))
#     print type(query_data)
#     print len(query_data.fetchall())