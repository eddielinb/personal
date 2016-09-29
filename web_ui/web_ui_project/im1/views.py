import json
# import urllib2

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

from web_ui_project.project_settings import app_list
from im.get_imGate import get_wave_data, get_appliance_map

# logging
import logging

time_unit_data = {
    'name': "time_unit",
    'choice_list':
        [
            {'value': 10, 'text': "Second", 'ch': ""},
            {'value': 20, 'text': "Minute", 'ch': "checked"},
            {'value': 25, 'text': "30 Minutes", 'ch': ""},
            {'value': 30, 'text': "Hour", 'ch': ""},
            {'value': 40, 'text': "Day", 'ch': ""},
            {'value': 50, 'text': "Month", 'ch': ""},
            {'value': 60, 'text': "Year", 'ch': ""},
        ]
    }

default_values = {
    'data_type': "observed_data",
    'customer': "0039_9000000002",
    # 'sts': 1465850300,
    'sts': 1465763880,
    'ets': 1465850360,
    'time_unit': [20],
    }

time_unit_map = {
    10: "Second",
    20: "Minute",
    25: "30 Minutes",
    30: "Hour",
    40: "Day",
    50: "Month",
    60: "Year",
}

previous_values = default_values.copy()

logger = logging.getLogger('web_ui.im')


def index(request):
    appliance_map_dump = json.dumps(get_appliance_map())
    time_map_dump = json.dumps(time_unit_map)
    context = {
        'app_list': app_list,
        'populate_values': default_values,
        'time_unit': time_unit_data,
        'time_map_str': time_map_dump,
        'app_map_str': appliance_map_dump,
    }
    return render(request, 'im1/index.html', context)


def post_data(request):
    json_data = {'wave_data': parse_request(request),
                 'headers': previous_values}
    data = json.dumps(json_data)
    return HttpResponse(data)


def json_response(request):
    return JsonResponse(parse_request(request))


def parse_request(request):
    settings = request.POST

    for key, item in settings.iterlists():
        if key in previous_values:
            if isinstance(previous_values[key], list):
                # previous_values[key] = settings.getlist(key)
                previous_values[key] = item
            elif len(item) == 1:
                previous_values[key] = item[0]
            else:
                raise Exception("parse_request:error1:{}".format(len(item)))
    try:
        return get_json()
    except IOError as e:
        logger.warning("im1.parse_request: %s", e)
        return {'error': "{!r}".format(e if not e.args else e.args[0])}
    except ValueError as e:
        logger.warning("im1.parse_request: %s", e)
        return {'error': "{!r}".format(e if not e.args else e.args[0])}


def get_json(data_type=None,
             customer=None,
             sts=None,
             ets=None,
             time_units=None):
    # This is necessary for some reason, if assigned directly it doesn't update and only a list of length 1 is retrieved
    data_type = data_type or previous_values['data_type']
    customer = customer or previous_values['customer']
    sts = sts or previous_values['sts']
    ets = ets or previous_values['ets']
    time_units = time_units or previous_values['time_unit']
    wave_data = get_wave_data(data_type, customer, sts, ets, time_units)
    return wave_data


# def main():
#     pass
#
# if __name__ == "__main__":
#     main()
