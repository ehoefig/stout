import logging

from pydispatch import dispatcher
from gateway import START_SIGNAL
from gateway import STOP_SIGNAL
from gateway.zigbee import ZigBeeAddress
from gateway.zigbee.zigbee_collector import ZIGBEE_RX_IO_DATA_LONG_ADDR
from gateway.zigbee.zigbee_collector import ZIGBEE_AT_RESPONSE
#from gateway.network import NEW_SENSOR_SIGNAL
#from gateway.network import SENSOR_METADATA_CHANGED
from gateway.network import NEW_DATA_SIGNAL
from gateway.network import sensors
from gateway.network import Sensor  # TODO subclass to make, e.g. ADXL335? Configure this?

__author__ = 'edzard'

logger = logging.getLogger(__name__)


def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    logger.debug("started")

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _identify_source_address(params):
    address = ZigBeeAddress(params['source_addr'], params['source_addr_long'])
    if address not in sensors:
        #logger.info("Found sensor with address {}".format(address))
        sensor = Sensor(address)
        # TODO: Add to sensors (use method from network)
        #dispatcher.send(signal=NEW_SENSOR_SIGNAL, sender=__name__, sensor=sensor)
    return address


def _data_handler(sender, **kwargs):
    # TODO Add location support
    # TODO Add type support
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    address = _identify_source_address(frame)
    for sample_tuple in frame['samples']:
        data = {'x': sample_tuple['adc-0'], 'y': sample_tuple['adc-1'], 'z': sample_tuple['adc-2']}
        dispatcher.send(signal=NEW_DATA_SIGNAL, sender=__name__, address=address, timestamp=timestamp, acceleration=data)

dispatcher.connect(_data_handler, signal=ZIGBEE_RX_IO_DATA_LONG_ADDR) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _command_handler(sender, **kwargs):
    frame = kwargs['frame']
    command = frame['command'].decode()
    if command == 'ND':
        parameter = frame['parameter']
        address = _identify_source_address(parameter)
        #sensor = sensors[address]
        # TODO: change sensor

        #dispatcher.send(signal=SENSOR_METADATA_CHANGED, sender=__name__, sensor=sensor, name=parameter['node_identifier'])
        # TODO What happens with more than one node?
        # TODO Use other information as well?
    else:
        logger.warning("Cannot handle command {}".format(command));

dispatcher.connect(_command_handler, signal=ZIGBEE_AT_RESPONSE) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _stop_handler(sender, **kwargs):
    logger.debug("stopped.")


