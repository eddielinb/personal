from django.shortcuts import render
from django.http import HttpResponse
from web_ui_project.project_settings import app_list

import sqlite3
import os
import json
# Create your views here.

default_values = {
    'data_type': "data",
    'mac': "0000000000000002",
    'sts': 1474815928,
    'ets': 1474902328,
}


def index(request):
    context = {
        'populate_values': default_values,
        'app_list': app_list,
    }
    return render(request, 'log_visual/index.html', context)


def post_data(request):
    data = retrieve_data_database()
    return json_response_data(data)


def json_response_data(data):
    data = {"wave_data": data}
    json_data = json.dumps(data)
    return HttpResponse(json_data)


def retrieve_data_database():
    cdir = os.path.abspath(os.path.dirname(__file__))
    conn = sqlite3.connect(os.path.join(cdir, '../database/webui.db'))
    request_count = []
    unique_mac_count = []
    hour_time = []
    for hour_ts in range(0, 3600*24, 3600):
        hour_time.append(default_values['sts'] + hour_ts)
        query_data = conn.execute("SELECT * FROM REQUEST WHERE TIMESTAMP > %s AND TIMESTAMP < %s;"
                                  % (str(hour_ts + default_values['sts']), str(hour_ts + 3600 + default_values['sts'])))
        query_data = query_data.fetchall()
        request_count.append(len(query_data))
        temp_unique_mac = []
        for row in query_data:
            if row[1] not in temp_unique_mac:
                temp_unique_mac.append(row[1])
        unique_mac_count.append(len(temp_unique_mac))
    conn.close()

    data = {"request_count": request_count, "unique_mac_count": unique_mac_count, "time_data": hour_time}
    return data

