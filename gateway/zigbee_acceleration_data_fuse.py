import logging
import binascii # TODO Why is pycharm showing an import error?
from gateway import START_SIGNAL
from gateway import STOP_SIGNAL
from gateway.zigbee_collector import ZIGBEE_FRAME_SIGNAL
from pydispatch import dispatcher

__author__ = 'edzard'

logger = logging.getLogger(__name__)


SENSOR_DATA_SIGNAL = 'new_sensor_data'


# TODO: override repr() to format up nicely when dumping out sensor data object
class ZigBeeAddress:

    def __init__(self, short, long):
        self.long = long
        self.short = short

    def __str__(self):
        return "{}({})".format(binascii.hexlify(self.short),binascii.hexlify(self.long))


def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    logger.debug("started")

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _frame_handler(sender, **kwargs):
    # TODO Add location support
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    assert frame['id'] is 'rx_io_data_long_addr' # Can only deal with these frames
    address = ZigBeeAddress(frame['source_addr'], frame['source_addr_long'])
    for sample_tuple in frame['samples']:
        data = {}
        data['x'] = sample_tuple['adc-0']
        data['y'] = sample_tuple['adc-1']
        data['z'] = sample_tuple['adc-2']
        dispatcher.send(signal=SENSOR_DATA_SIGNAL, sender=__name__, address=address, timestamp=timestamp, acceleration=data)

dispatcher.connect(_frame_handler, signal=ZIGBEE_FRAME_SIGNAL) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _stop_handler(sender, **kwargs):
    logger.debug("stopped.")


