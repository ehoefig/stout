import binascii
import logging
from pydispatch import dispatcher
from struct import unpack
from gateway.network import SENSOR_METADATA_CHANGED
from gateway.sensors import Sensor

__author__ = 'edzard'

logger = logging.getLogger(__name__)  # TODO: is that ok?


class ZigBeeAddress:
    """
    Stores a single zigbee address consisting of a 16bit short network address, and a longer 64bit IEEE Mac address.
    """

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


class ZigBeeSensor(Sensor):
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


# TODO FEATURE generic base class for RX frame based sensors?
class BNO055(ZigBeeSensor):

    def __init__(self, address,  name=None, location=None):
        super().__init__(address, name=name, kind='BNO055', location=location)

    def convert(self, data):
        ow, ox, oy, oz, ax, ay, az = unpack('hhhhhhh', data)
        orientation = {'w': ow/(1 << 14), 'x': ox/(1 << 14), 'y': oy/(1 << 14), 'z': oz/(1 << 14)}
        linear_acceleration = {'x': ax/100, 'y': ay/100, 'z': az/100}
        return orientation, linear_acceleration

    def get_num_samples_per_frame(self):
        return 5

    def get_sampling_frequency(self):   # Hz
        return 20


class ADXL335(ZigBeeSensor):

    def __init__(self, address,  name=None, location=None):
        super().__init__(address, name=name, kind='ADXL335', location=location)

    def convert(self, data):
        # TODO FEATURE generic unpacking of IO sample data
        x,y,z = data['adc-0'], data['adc-1'], data['adc-2']
        # TODO Proper scaling of values
        return {'x': x/1, 'y': y/1, 'z': z/1}
