import logging
from pydispatch import dispatcher
from gateway import START_SIGNAL
from gateway import STOP_SIGNAL

__author__ = 'edzard'

NEW_SENSOR_SIGNAL = 'new_sensor'
NEW_DATA_SIGNAL = 'new_data'
SENSOR_METADATA_CHANGED = 'sensor_metadata_changed'

logger = logging.getLogger(__name__) # TODO: is that ok?

sensors = {}


# TODO add "unit" field?
class Sensor:
    """
    Stores information about a single network.
    """

    def __init__(self, address):
        self.address = address
        self.type = None
        self.name = None
        self.location = None

    def __str__(self):
        return "{} sensor with address {} of {} type at {}".format(
            'Unnamed' if self.name is None else self.name, self.address, 'unknown' if self.type is None else self.type,
            'unknown location' if self.location is None else self.location)

    def __eq__(self, other):
        return self.address.__eq__(other.address)

    def __hash__(self):
        return self.address.__hash__()


# if identifier is not None:
#     sensor_identifier[address] = identifier.decode()
#     logger.info("Sensor at address {} is known as '{}'".format(address, sensor_identifier[address]))

# TODO: supply methods for adding, removing(?) and changing sensors. These have to trigger the appropriate events

def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    logger.debug("started")

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _stop_handler(sender, **kwargs):
    logger.debug("stopped.")
