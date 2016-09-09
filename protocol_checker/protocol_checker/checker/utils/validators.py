import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_mac(mac_address):
    """Validate mac_address xxxxxxxxxxxxxxxx or xxxxxxxxxxxxxxxx/y.
    if mac_address is invalid, raise ValidationError.
    :param mac_address: target macaddress
    :type mac_address: str
    :raise InvalidParameterError: if mac address is invalid.
    """
    try:
        macs = mac_address.split('/')
        mac = macs[0]
        if re.compile("^[0-9A-Fa-f]+$").match(mac) is None or len(mac) != 16:
            raise Exception
        if len(macs) > 1:
            channel_id_is_valid(int(macs[1]))
        return True
    except:
        raise ValidationError(
            _('%(value)s is not a valid mac address'),
            params={'value': mac_address},
        )


def channel_id_is_valid(ch_id):
    """
    validate channel id. if channel id is invalid, raise ValidationError.
    :type ch_id: int
    :param ch_id: channel index
    :return: only the case of valid returns True.
    """
    try:
        if not isinstance(ch_id, int) or ch_id <= 0:
            raise Exception
        return True
    except:
        raise ValidationError(
            _('%(value)s is not a valid channel id'),
            params={'value': ch_id},
        )
