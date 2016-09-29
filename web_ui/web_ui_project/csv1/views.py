import json
import os
import StringIO

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

from modules.common.utils import to_datetime
from modules.gcp.google_drive import GoogleDrive
from web_ui_project.project_settings import app_list, GOOGLE_CREDENTIALS_FILE

# logging
import logging

LOCAL_DIR = '/'
TESTING_DIR = "/home/droogmic/csv_files"

default_values = {
    'data_type': "estimated_data",
    'service_id': "0006",
    'user_id': "0000000001",
    # 'ts': 1463702400,
    'ts': 1467298800,
    'tz': "Asia/Tokyo",
}
previous = default_values.copy()

logger = logging.getLogger('web_ui.csv')


def index(request):
    context = {
        'populate_values': default_values,
        'app_list': app_list,
    }
    return render(request, 'csv1/index.html', context)


def json_response(request):
    return JsonResponse(parse_request(request))


def post_data(request):
    json_data = {'wave_data': parse_request(request),
                 'headers': previous}
    data = json.dumps(json_data)
    return HttpResponse(data)


def parse_request(request):
    settings = request.POST
    for key, item in settings.iterlists():
        if key in previous:
            if isinstance(previous[key], list):
                previous[key] = item
            elif len(item) == 1:
                previous[key] = item[0]
            else:
                raise Exception("parse_request:error1:{}".format(len(item)))
        else:
            pass
    try:
        return get_json()
    except IOError as e:
        logger.warning("csv1.parse_request: %s", e)
        return {'error': "{!r}".format(e.args[0])}
    except ValueError as e:
        logger.warning("csv1.parse_request: %s", e)
        return {'error': "{!r}".format(e.args[0])}


def get_json(data_type=None,
             service_id=None,
             user_id=None,
             ts=None,
             tz=None):
    data_type = data_type or previous['data_type']
    service_id = service_id or previous['service_id']
    user_id = user_id or previous['user_id']
    ts = ts or int(previous['ts'])
    tz = tz or previous['tz']

    # Validation
    if not isinstance(data_type, basestring):
        raise ValueError("data_type is of {}, should be of type {}".format(type(data_type), "str"))
    if not isinstance(service_id, basestring):
        raise ValueError("service_id is of {}, should be of type {}".format(type(service_id), "str"))
    if not isinstance(user_id, basestring):
        raise ValueError("user_id is of {}, should be of type {}".format(type(user_id), "str"))
    if not isinstance(ts, int):
        raise ValueError("ts is of {}, should be of type {}".format(type(ts), "int"))
    if not isinstance(tz, basestring):
        raise ValueError("tz is of {}, should be of type {}".format(type(tz), "str"))

    if len(user_id) != 10:
        raise ValueError("user_id is of length {}, should be of length {}".format(len(user_id), 10))

    # return _get_local_csv(data_type, service_id, user_id, ts, tz)
    # return _get_local_csv(data_type, service_id, user_id, 1463702400, tz)
    return _get_google_drive_csv(data_type, service_id, user_id, ts, tz)


def _get_google_drive_csv(data_type,
                          service_id,
                          user_id,
                          ts,
                          tz):
    dt = to_datetime(ts, tz)
    _obs = "_obs" if data_type == "observed_data" else ""
    file_name = "{}_{}{_observed}.csv".format(dt.strftime("%Y%m%d"), user_id, _observed=_obs)
    file_dir = [
        str(service_id),
        str(user_id)[0:2],
        str(user_id)[2:4],
        str(user_id)[4:6],
        str(user_id)[6:8],
        str(user_id)[8:10],
        dt.strftime("%Y"),
        dt.strftime("%m"),
    ]
    logger.info("Downloading file %s/%s", "/".join(file_dir), file_name)

    gd = GoogleDrive(GOOGLE_CREDENTIALS_FILE)
    fids = gd.retrieve_all_files(file_name, file_dir, parent_ids=[])
    if fids:
        data_bytes = gd.download_file(fids[0]['id'])
    else:
        raise IOError("No google drive file found", "fids={}, file_name={}, file_dir={}".format(fids, file_name, file_dir))

    data_string = data_bytes.decode()
    string_buffer = StringIO.StringIO(data_string)
    return _populate_dict(string_buffer)


def _get_local_csv(data_type,
                   service_id,
                   user_id,
                   ts,
                   tz):

    dt = to_datetime(ts, tz)
    _obs = "_obs" if data_type == "observed_data" else ""
    file_name = "{}_{}{_observed}.csv".format(dt.strftime("%Y%m%d"), user_id, _observed=_obs)

    file_dir = TESTING_DIR or os.path.join(LOCAL_DIR,
                                           str(service_id),
                                           str(user_id)[0:2],
                                           str(user_id)[2:4],
                                           str(user_id)[4:6],
                                           str(user_id)[6:8],
                                           str(user_id)[8:10],
                                           dt.strftime("%Y"),
                                           dt.strftime("%m"))
    d = os.path.join(file_dir, file_name)
    logger.info("File loaded: %s", d)

    with open(d) as read_file:
        data_dict = _populate_dict(read_file)

    return data_dict


def _populate_dict(file_object):
    """
    dict returned:
    {
        'mac': data_line_symbols[2],
        'data': {
            'timestamps': [int(data_line_symbols[0])],
            'root_powers': [float(data_line_symbols[1])],
            'apps': [
                {
                    'app_type_id': 10,
                    'app_id': -1,
                    'app_type_name': Fridge,
                    'app_powers': 11.9,
                },
                {...},
                ...
            ],
        }
    }
    :param file_object:
    :return:
    """
    data_line = file_object.readline()
    data_line.rstrip('\n')
    data_line_symbols = data_line.split(',')
    if data_line != "" and '' not in data_line_symbols[0:3]:
        data_dict = {
            'mac': data_line_symbols[2],
            'data': {
                'timestamps': [int(data_line_symbols[0])],
                'root_powers': [float(data_line_symbols[1])],
                'apps': [],
            },
        }
        len_data_line_symbols = len(data_line_symbols)
        for i in range(3, len(data_line_symbols), 4):
            if '' not in data_line_symbols[i:i+4]:
                app = {
                    'app_type_id': data_line_symbols[i],
                    'app_id': data_line_symbols[i + 1],
                    'app_type_name': data_line_symbols[i + 2],
                    'app_powers': [float(data_line_symbols[i + 3])],
                }
                data_dict['data']['apps'].append(app)
            else:
                len_data_line_symbols = i+1  # If empty appliance
                break

        data_line = file_object.readline()
        while data_line != "":
            data_line.rstrip('\n')
            data_line_symbols = data_line.split(',')
            if '' not in data_line_symbols[0:2]:
                data_dict['data']['timestamps'].append(int(data_line_symbols[0]))
                data_dict['data']['root_powers'].append(float(data_line_symbols[1]))
                if data_dict['data']['apps']:
                    for count, i in enumerate(range(6, len_data_line_symbols, 4)):
                        if '' not in data_line_symbols[i:i+4]:
                            data_dict['data']['apps'][count]['app_powers'].append(float(data_line_symbols[i]))
            data_line = file_object.readline()
    else:
        data_dict = {'error': "Error: Empty file"}
    return data_dict


# def main():
#
#
# if __name__ == "__main__":
#     main()
