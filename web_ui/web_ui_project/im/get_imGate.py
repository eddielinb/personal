import urllib2
import json

from im.imgate_settings import IMGATE_API_SETTINGS
from im.internal_api_settings import INTERNAL_API_SETTINGS

# logging
import logging
logger = logging.getLogger('web_ui.im')

cache_appliance_map = None

def get_wave_data(data_type,
                  customer,
                  sts,
                  ets,
                  time_units):

    time_unit_string = ""
    for time_unit in time_units:
        time_unit_string += "&time_units[]={}".format(time_unit)

    # url = "http://104.155.192.173:3000/0.1/{data_type}?customer={cust}&sts={sts}&ets={ets}{time_unit_str}"\
    #     .format(data_type=data_type, cust=customer, sts=sts, ets=ets, time_unit_str=time_unit_string)
    url = "http://{ip}:{port}/{version}/{data_type}?customer={cust}&sts={sts}&ets={ets}{time_unit_str}".format(
        data_type=data_type, cust=customer, sts=sts, ets=ets, time_unit_str=time_unit_string,
        **IMGATE_API_SETTINGS)

    logger.info("Requesting: %s",url)

    req = urllib2.Request(url, headers={'Authorization': "imSP 0039:UCaiRyCInM8zilx5xKV5"})

    result = urllib2.urlopen(req, timeout=IMGATE_API_SETTINGS['timeout'])
    # result.read() will contain the data
    # result.info() will contain the HTTP headers
    wave_data = json.load(result)

    if not wave_data['data']:
        raise IOError("Invalid data retrieved")

    return wave_data


def _get_appliance_id_map():

    url = "http://{ip}:{port}/{version}/{data_type}".format(
        data_type="get_appliance_type_list",
        **INTERNAL_API_SETTINGS)

    logger.info("Requesting: %s",url)

    req = urllib2.Request(url, headers={'Authorization': "imSP 0039:UCaiRyCInM8zilx5xKV5"})

    result = urllib2.urlopen(req, timeout=INTERNAL_API_SETTINGS['timeout'])

    map_data = json.load(result)

    if not map_data or not isinstance(map_data, dict):
        raise IOError("Invalid data retrieved: {}".format(map_data))

    return map_data


def get_appliance_map():
    global cache_appliance_map
    if cache_appliance_map is None:
        cache_appliance_map = _get_appliance_id_map()
    return cache_appliance_map


def get_appliance_name(appliance_id):
    return _get_appliance_att(u'name', appliance_id)


def get_appliance_type(appliance_id):
    return _get_appliance_att(u'type', appliance_id)


def _get_appliance_att(key, appliance_id):
    _appliance_map = get_appliance_map()
    appliance = _appliance_map.get(str(appliance_id))
    if appliance is None:
        raise ValueError("get_appliance_name appliance_id not valid: {}".format(appliance_id))
    return appliance[key]
