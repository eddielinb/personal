import json

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

from modules.gcp.waves import Waves
from web_ui_project.project_settings import app_list, GOOGLE_CREDENTIALS_FILE

# logging
import logging

GOOGLE_PARENT_ID = "0B7-tDKsp2J8JUnF6b1Q2eWhEZEE"

default_values = {
    'data_type': "data",
    'mac': "98F170FFFEFBB782",
    'sts': 1469307600,
    'ets': 1469318400,
}
previous = default_values.copy()

logger = logging.getLogger('web_ui.gdrive')


def index(request):
    context = {
        'populate_values': default_values,
        'app_list': app_list,
    }
    return render(request, 'gdrive1/index.html', context)


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
                raise Exception("parse_request:error1:len:{}".format(len(item)))
        else:
            if key != "csrfmiddlewaretoken":
                raise Exception("parse_request:error2:keyerror:{}".format(key))
    try:
        return get_json()
    except IOError as e:
        logger.warning("gdrive1.parse_request: %s", e)
        return {'error': "{!r}".format(e.args[0])}
    except ValueError as e:
        logger.warning("gdrive1.parse_request: %s", e)
        return {'error': "{!r}".format(e.args[0])}


def get_json(mac=None,
             sts=None,
             ets=None):
    mac = mac or previous['mac']
    sts = sts or int(previous['sts'])
    ets = ets or int(previous['ets'])

    waves_object = Waves(GOOGLE_CREDENTIALS_FILE, GOOGLE_PARENT_ID)
    data_dict = waves_object.download_waves(mac, sts)
    if data_dict is None:
        raise ValueError("No data found")

    for ts in range(sts + 3600, ets, 3600):
        logger.info("Getting waves from GCP with mac=%s, ts=%s", mac, ts)
        temp_dict = waves_object.download_waves(mac, ts)
        if temp_dict is None:
            raise ValueError("No data found")
        data_dict['timestamps'].extend(temp_dict['timestamps'])
        data_dict['rssi'].extend(temp_dict['rssi'])
        data_dict['voltages'].extend(temp_dict['voltages'])
        for channel_index, channel_data in enumerate(data_dict['data']):
            channel_data['root_powers'].extend(temp_dict['data'][channel_index]['root_powers'])
            channel_data['waves'].extend(temp_dict['data'][channel_index]['waves'])
        data_dict['logs'].update(temp_dict['logs'])

    return data_dict


# def main():
#     pass
#     get_json()
#
# if __name__ == "__main__":
#     main()
