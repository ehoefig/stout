import logging

from pydispatch import dispatcher

from gateway import START_SIGNAL
from gateway import STOP_SIGNAL
from gateway.zigbee import Address
from gateway.zigbee.zigbee_collector import ZIGBEE_RX_IO_DATA_LONG_ADDR
from gateway.zigbee.zigbee_collector import ZIGBEE_AT_RESPONSE

__author__ = 'edzard'

logger = logging.getLogger(__name__)


SENSOR_DATA_SIGNAL = 'new_sensor_data'

network = set()         # contains addresses
sensor_identifier = {}  # contains address -> name mapping


def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    logger.debug("started")

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _identify_source_address(params, identifier=None):
    address = Address(params['source_addr'], params['source_addr_long'])
    if address not in network:
        network.add(address)
        logger.info("Found sensor with address {}".format(address))
    if identifier is not None:
        sensor_identifier[address] = identifier.decode()
        logger.info("Sensor at address {} is known as '{}'".format(address, sensor_identifier[address]))
    return address


def _data_handler(sender, **kwargs):
    # TODO Add location support
    # TODO Add type support
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    address = _identify_source_address(frame)
    for sample_tuple in frame['samples']:
        data = {'x': sample_tuple['adc-0'], 'y': sample_tuple['adc-1'], 'z': sample_tuple['adc-2']}
        dispatcher.send(signal=SENSOR_DATA_SIGNAL, sender=__name__, address=address, timestamp=timestamp, acceleration=data)

dispatcher.connect(_data_handler, signal=ZIGBEE_RX_IO_DATA_LONG_ADDR) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _command_handler(sender, **kwargs):
    frame = kwargs['frame']
    command = frame['command'].decode()
    if command == 'ND':
        parameter = frame['parameter']
        _identify_source_address(parameter, parameter['node_identifier'])   # This remembers the identifier
        # TODO What happens with more than one node?
        # TODO Use other information as well?
    else:
        logger.warning("Cannot handle command {}".format(command));

dispatcher.connect(_command_handler, signal=ZIGBEE_AT_RESPONSE) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _stop_handler(sender, **kwargs):
    logger.debug("stopped.")


