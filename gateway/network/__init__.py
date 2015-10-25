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
