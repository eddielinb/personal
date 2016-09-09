import logging
import signal
import re
import base64
import hashlib


class InvalidParameterError(Exception):
    pass


msg = "The signature you provided does not match the signature we calculated."
protocol_errors = {
"SignatureDoesNotMatch":{
    'code': "SignatureDoesNotMatch",
    'message': msg,
    'http_status': 403
},
"ActivationNotAllowed":{
    'code': "ActivationNotAllowed",
    'message': "The activation is not allowed.",
    'http_status': 403
},
"SignatureTimeout" : {
    'code': "SignatureTimeout",
    'message': "The signature you provided is unavailable due to timeout.",
    'http_status': 403
},
"InvalidAccessKey" : {
    'code': "InvalidAccessKey",
    'message': "The access key you provided does not exist in our records.",
    'http_status': 403
},
"ConnectionError" :{
    'code': "ConnectionError",
    'message': "there is connection error between cliend and server",
    'http_status':403
},
"BadRequest":{
    'code': "BadRequest",
    'message': "The request you provided is not valid.",
    'http_status': 400
},
"FirmwareNotFound" :{
    'code': "FirmwareNotFound",
    'message': "The firmware you requested is not found.",
    'http_status': 400
},

"InternalServerError":{
    'code': "InternalServerError",
    'message': "The internal server error occurred.",
    'http_status': 500
}
}

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
        if re.compile("^[0-9A-Fa-f]+$").match(mac) is None or\
                        len(mac) != 16:
            raise
        if len(macs) > 1:
            channel_id_is_valid(int(macs[1]))
        return True
    except:
        raise InvalidParameterError("validator:_validate_mac_address:%s" %
                                    mac_address)


def create_secret_activation_key(auth_type, lid, seed):
    """
    Creates secret activation key from SAK seed.

    Args:
        auth_type: must be "imAuth"
        lid: lavender ID
        seed: SAK seed
    """
    lid = lid.upper()
    txt = lid + ":" + seed
    return base64.encodestring(hashlib.sha256(txt).digest()).strip()[:40]


class SignalHandler(object):
    def __init__(self):
        # signaling properties
        self._sigint = False
        self._sighup = False
        self._sigterm = False
        self._signal_logger = logging.getLogger(self.__class__.__name__)

    @property
    def sigint(self):
        return self._sigint

    @property
    def sighup(self):
        return self._sighup

    @property
    def sigterm(self):
        return self._sigterm

    def signaled(self):
        return self.sigterm or self.sigint or self.sighup

    def on_sigint(self, sig, fem):
        self._signal_logger.info("SIGINT")
        self._sigint = True

    def on_sighup(self, sig, fem):
        self._signal_logger.info("SIGHUP")
        self._sighup = True

    def on_sigterm(self, sig, fem):
        self._signal_logger.info("SIGTERM")
        self._sigterm = True

    def register_signals(self, signals):
        for sig in signals:
            if sig == signal.SIGHUP:
                signal.signal(signal.SIGHUP, self.on_sighup)
            elif sig == signal.SIGTERM:
                signal.signal(signal.SIGTERM, self.on_sigterm)
            elif sig == signal.SIGINT:
                signal.signal(signal.SIGINT, self.on_sigint)
            else:
                self._signal_logger.warn("unsupported signal: %s" % sig)
