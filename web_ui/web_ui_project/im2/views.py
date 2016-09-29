import json
# import urllib2

# from django.http import HttpResponse
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template import loader

from web_ui_project.project_settings import app_list
from im.get_imGate import get_wave_data, get_appliance_map, get_appliance_name, get_appliance_type

# logging
import logging

default_values = {
    'data_type': "data",
    'customer': "0039_9000000002",
    # 'sts': 1465850300,
    'sts': 1465763880,
    'ets': 1465850360,
    'time_unit': [20],
}
previous_values = default_values.copy()

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

time_unit_map = {}
for choice in time_unit_data['choice_list']:
    time_unit_map[choice['value']] = choice['text']

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
    return render(request, 'im2/index.html', context)


def post_data(request):
    parse_request = request.POST
    if "calculate" in parse_request["data_type"]:
        dict_data = calculate_matching(parse_request)
        return JsonResponse(dict_data)
    else:
        wave_data = wave_data_request(parse_request)
        appliance_list = wave_data['estimated_data'][u'data'][0][u'appliance_types']
        seen = set()
        unique_appliance_list = [app for app in appliance_list if
                                 app[u'appliance_type_id'] not in seen and not seen.add(app[u'appliance_type_id'])]
        html = """"""
        graph_count = len(unique_appliance_list)
        for appliance_index, appliance in enumerate(unique_appliance_list):
            c = {
                'graph_id': "graph" + str(appliance_index),
                'graph_num': "Num" + str(appliance_index),
                'graph_title': "{}, {}:{}".format(get_appliance_name(appliance[u'appliance_type_id']),
                                                  appliance[u'appliance_type_id'],
                                                  get_appliance_type(appliance[u'appliance_type_id'])),
            }
            html += loader.render_to_string('im2/graph.html', context=c)
        dict_data = {
            'wave_data': wave_data,
            'headers': previous_values,
            'graph_html': html,
            'graph_count': graph_count,
        }
        return JsonResponse(dict_data)


def wave_data_request(settings):
    for key, item in settings.iterlists():
        if key in previous_values:
            if isinstance(previous_values[key], list):
                previous_values[key] = item
            elif len(item) == 1:
                previous_values[key] = item[0]
            else:
                raise Exception("parse_request:error1:{}".format(len(item)))
    try:
        return {
            'observed_data': get_json(data_type='observed_data'),
            'estimated_data': get_json(data_type='estimated_data')
        }
    except IOError as e:
        logger.warning("im2.parse_request: %s", e)
        return {'error': "{!r}".format(e if not e.args else e.args[0])}
    except ValueError as e:
        logger.warning("im2.parse_request: %s", e)
        return {'error': "{!r}".format(e if not e.args else e.args[0])}


def calculate_matching(post_request):

    # To do the calculation here
    # post_request is the query dict containing the posted data from client
    temp_values = {'calculation': True, 'f_measure': 1, 'matching_rate': 0.5}
    return temp_values


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
#     # estimated_data = get_json(data_type='estimated_data')
#     # observed_data = get_json(data_type='observed_data')
#     # print get_appliance_id_map()
#     pass
#
# if __name__ == "__main__":
#     main()
