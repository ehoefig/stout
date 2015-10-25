import binascii
import logging
from pydispatch import dispatcher
from gateway.network import Sensor, SENSOR_METADATA_CHANGED

__author__ = 'edzard'

logger = logging.getLogger(__name__)  # TODO: is that ok?


def _create_from_hex(str_address):
        return ZigBeeAddress(binascii.unhexlify(str_address))


class ZigBeeAddress:
    """
    Stores a single zigbee address consisting of a 16bit short network address, and a longer 64bit IEEE Mac address.
    """

    from_hex_string = _create_from_hex

    def __init__(self, mac_address, network_address=None):
        self.mac_address, self.network_address = mac_address, network_address

    def __str__(self):
        if self.network_address is None:
            return binascii.hexlify(self.mac_address).decode().upper()
        else:
            return "{}/{}".format(binascii.hexlify(self.mac_address).decode().upper(),
                                  binascii.hexlify(self.network_address).decode().upper())

    def __repr__(self):
        return "gateway.zigbee.ZigBeeAddress({}, {})".format(self.mac_address, self.network_address)

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, ZigBeeAddress):
            return self.mac_address == other.mac_address
        else:
            return False

    def __hash__(self):
        return hash(self.mac_address)


class ZigBeeSensor(Sensor):
    """
    Contains the specifics for ZigBee Sensors
    """
    
    def __init__(self, address, kind=None, name=None, location=None):
        super(ZigBeeSensor, self).__init__(address, kind, location)
        self.__name = name

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        logger.debug("Changing sensor {} name from {} to {}".format(self.address, self.name, value))
        self.__name = value
        dispatcher.send(signal=SENSOR_METADATA_CHANGED, sender=__name__, sensor=self, name=self.name)

    def __str__(self):
        return "{} zigbee sensor with address {} of {} kind at {}".format(
            'Unnamed' if self.name is None else self.name, self.address, 'unknown' if self.kind is None else self.kind,
            'unknown location' if self.location is None else self.location)

    def __repr__(self):
        return "gateway.zigbee.ZigBeeSensor({}, {}, {}, {})".format(self.address, self.kind, self.name, self.location)

