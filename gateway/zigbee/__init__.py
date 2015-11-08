import binascii
import logging
from pydispatch import dispatcher
from gateway.network import SENSOR_METADATA_CHANGED
from gateway.sensors import BaseSensor

__author__ = 'edzard'

logger = logging.getLogger(__name__)  # TODO: is that ok?


class ZigBeeAddress:
    """
    Stores a single zigbee address consisting of a 16bit short network address, and a longer 64bit IEEE Mac address.
    """

    # @staticmethod
    # def from_hex_string(str_address):
    #     return ZigBeeAddress(binascii.unhexlify(str_address))

    def as_hex(self):
        return binascii.hexlify(self._mac_address).decode().upper()

    def __init__(self, mac_address, network_address=None):
        self._mac_address, self._network_address = mac_address, network_address
        self._hex_mac_address = binascii.hexlify(self._mac_address).decode().upper()
        self._hex_network_address = binascii.hexlify(self._network_address).decode().upper()

    def __str__(self):
        return "zigbee <{}/{}>".format(self._hex_mac_address, self._hex_network_address)

    def __repr__(self):
        return "gateway.zigbee.ZigBeeAddress({}, {})".format(self._mac_address, self._network_address)

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, ZigBeeAddress):
            return self._mac_address == other._mac_address
        else:
            return False

    def __hash__(self):
        return hash(self._mac_address)


class ZigBeeBaseSensor(BaseSensor):
    """
    Contains the specifics for ZigBee Sensors
    """
    
    def __init__(self, address, name=None, kind=None, location=None):
        super().__init__(address, kind=kind, location=location)
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        logger.debug("Changing sensor {} name from {} to {}".format(self.address, self.name, value))
        self._name = value
        dispatcher.send(signal=SENSOR_METADATA_CHANGED, sender=__name__, sensor=self, name=self.name)

    def __str__(self):
        if self.name is None:
            return self.address
        else:
            return self.name

    def __repr__(self):
        return "gateway.zigbee.ZigBeeSensor({}, {}, {}, {})".format(self.address, self.kind, self.name, self.location)


class BNO055(ZigBeeBaseSensor):

    def __init__(self, address,  name=None, location=None):
        super().__init__(address, name=name, kind='BNO055', location=location)

    def convert(self, data):
        pass


class ADXL335(ZigBeeBaseSensor):

    def __init__(self, address,  name=None, location=None):
        super().__init__(address, name=name, kind='ADXL335', location=location)

    def convert(self, data):
        pass