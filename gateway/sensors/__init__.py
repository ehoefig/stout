import logging
from pydispatch import dispatcher
from gateway.network import logger, SENSOR_METADATA_CHANGED

__author__ = 'edzard'


logger = logging.getLogger(__name__)


# TODO add "unit" field?

class Sensor:
    """
    Stores information about a single network.
    """

    def __init__(self, address, kind=None, location=None):
        self._address = address
        self._kind = kind #kwargs.get('kind', None)
        self._location = location #kwargs.get('location', None)

    @property
    def address(self):
        return self._address

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, value):
        logger.debug("Changing sensor {} kind from {} to {}".format(self.address, self.kind, value))
        self._kind = value
        dispatcher.send(signal=SENSOR_METADATA_CHANGED, sender=__name__, sensor=self, kind=self.kind)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        logger.debug("Changing sensor {} location from {} to {}".format(self.address, self.location, value))
        self._location = value
        dispatcher.send(signal=SENSOR_METADATA_CHANGED, sender=__name__, sensor=self, location=self.location)

    def __str__(self):
        return "Sensor with address {} of {} kind at {}".format(
            self.address, 'unknown' if self.kind is None else self.kind,
            'unknown location' if self.location is None else self.location)

    def __repr__(self):
        return "gateway.network.Sensor({}, {}, {})".format(self.address, self.kind, self.location)

    def __eq__(self, other):
        return self.address.__eq__(other.address)

    def __hash__(self):
        return self.address.__hash__()