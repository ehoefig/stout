import logging
from pydispatch import dispatcher
from gateway import START_SIGNAL
from gateway import STOP_SIGNAL

__author__ = 'edzard'

SENSOR_DISCOVERED = 'discovered_sensor'
SENSOR_LOST = 'lost_sensor'
SENSOR_METADATA_CHANGED = 'sensor_metadata_changed'
NEW_DATA_SIGNAL = 'new_data'

logger = logging.getLogger(__name__)

_sensors = {}


# TODO add "unit" field?
class Sensor:
    """
    Stores information about a single network.
    """

    def __init__(self, address, kind=None, location=None):
        self.__address = address
        self.__kind = kind
        self.__location = location

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, value):
        # Read-only value
        pass

    @property
    def kind(self):
        return self.__kind

    @kind.setter
    def kind(self, value):
        logger.debug("Changing sensor {} kind from {} to {}".format(self.address, self.kind, value))
        self.__kind = value
        dispatcher.send(signal=SENSOR_METADATA_CHANGED, sender=__name__, sensor=self, kind=self.kind)

    @property
    def location(self):
        return self.__location

    @location.setter
    def location(self, value):
        logger.debug("Changing sensor {} location from {} to {}".format(self.address, self.location, value))
        self.__location = value
        dispatcher.send(signal=SENSOR_METADATA_CHANGED, sender=__name__, sensor=self, location=self.location)

    def __str__(self):
        return "Sensor with address {} of {} kind at {}".format(self.address,
            'unknown' if self.kind is None else self.kind,
            'unknown location' if self.location is None else self.location)

    def __repr__(self):
        return "gateway.network.Sensor({}, {}, {})".format(self.address, self.kind, self.location)

    def __eq__(self, other):
        return self.address.__eq__(other.address)

    def __hash__(self):
        return self.address.__hash__()


class UnknownSensorException(Exception):
    pass


def get_network():
    return _sensors.values()


def has_sensor_for_address(address):
    return address in _sensors


def get_sensor(address):
    if address in _sensors:
        return _sensors[address]
    else:
        logger.debug("Queried for unknown sensor with address {}".format(address))
        raise UnknownSensorException("No known sensor with address {}".format(address))


def remove_sensor(address):
    if address in _sensors:
        logger.debug("Sensor with address {} removed from network".format(address))
        sensor = _sensors.pop(address)
        dispatcher.send(signal=SENSOR_LOST, sender=__name__, sensor=sensor)


def add_sensor(sensor):
    if sensor.address not in _sensors:
        logger.debug("Sensor with address {} added to network".format(sensor.address))
        _sensors[sensor.address] = sensor
        dispatcher.send(signal=SENSOR_DISCOVERED, sender=__name__, sensor=sensor)


def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    logger.debug("started")


dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _stop_handler(sender, **kwargs):
    logger.debug("stopped.")
