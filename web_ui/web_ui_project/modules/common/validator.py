import re


class ImCloudError(Exception):
    pass


class InvalidParameterError(ImCloudError):
    pass


def mac_is_valid(mac_address):
    """Validate mac_address xxxxxxxxxxxxxxxx or xxxxxxxxxxxxxxxx/y.
    if mac_address is invalid, raise InvalidParameterError.
    :param mac_address: target macaddress
    :type mac_address: str
    :raise InvalidParameterError: if mac address is invalid.
    """
    try:
        macs = mac_address.split('/')
        mac = macs[0]
        if re.compile("^[0-9A-Fa-f]+$").match(mac) is None or len(mac) != 16:
            raise
        if len(macs) > 1:
            channel_id_is_valid(int(macs[1]))
        return True
    except:
        raise InvalidParameterError("validator:_validate_mac_address:%s" %
                                    mac_address)


def timestamp_is_valid(timestamp):
    """
    validate timestamp. if timestamp is invalid, raise InvalidParameterError.
    :type timestamp: int
    :param timestamp: timestamp
    :return: only the case of valid returns True.
    """
    try:
        if not isinstance(timestamp, int) and \
                not isinstance(timestamp, long) or \
                timestamp < 0 or timestamp >= 2 ** 32:
            raise
        return True
    except:
        raise InvalidParameterError("validator:_validate_timestamp:%s" %
                                    timestamp)


def channel_id_is_valid(ch_id):
    """
    validate channel id. if channel id is invalid, raise InvalidParameterError.
    :type ch_id: int
    :param ch_id: channel index
    :return: only the case of valid returns True.
    """
    try:
        if not isinstance(ch_id, int) or ch_id <= 0:
            raise
        return True
    except:
        raise InvalidParameterError("validator:_validate_ch_id:%s" % ch_id)


def zoom_is_valid(zoom):
    """
    validate zoom. zoom must be 'minute', 'hour', '6hours', 'day', 'week', 'month' or 'year'.
    :type zoom: str
    :param zoom: zoom parameter
    :return:
    """
    if zoom not in ['minute', 'hour', '6hours', 'day',
                    'week', 'month', 'year']:
        raise InvalidParameterError("S3Base:_validate_zoom:%s" % zoom)
    return True
