from pydispatch import dispatcher
from gateway import START_SIGNAL, STOP_SIGNAL, zigbee
from gateway.zigbee import ZigBeeAddress, ZigBeeSensor
from gateway.zigbee.zigbee_collector import ZIGBEE_RX_IO_DATA_LONG_ADDR, ZIGBEE_AT_RESPONSE
from gateway.network import NEW_DATA_SIGNAL, add_sensor, get_sensor, has_sensor_for_address

__author__ = 'edzard'

logger = zigbee.logger

map = {}


def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    logger.debug("ZigBee sensor manager started")

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _identify_source_address(params):
    address = ZigBeeAddress(params['source_addr_long'], params['source_addr'])
    if has_sensor_for_address(address):
        sensor = get_sensor(address)
    else:
        # Create a new one
        sensor = ZigBeeSensor(address)
        add_sensor(sensor)
        logger.debug("ZigBee sensor with address {} created".format(address))
        # Do we know the type?
        if address in map:
            sensor.kind = map[address]
    return sensor


def _data_handler(sender, **kwargs):
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    sensor = _identify_source_address(frame)
    for sample_tuple in frame['samples']:
        # TODO use sensor map to access sensor data
        data = {'x': sample_tuple['adc-0'], 'y': sample_tuple['adc-1'], 'z': sample_tuple['adc-2']}
        dispatcher.send(signal=NEW_DATA_SIGNAL, sender=__name__, sensor=sensor, timestamp=timestamp, acceleration=data)

dispatcher.connect(_data_handler, signal=ZIGBEE_RX_IO_DATA_LONG_ADDR) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _command_handler(sender, **kwargs):
    frame = kwargs['frame']
    command = frame['command'].decode()
    if command == 'ND':
        parameter = frame['parameter']
        sensor = _identify_source_address(parameter)
        sensor.name = parameter['node_identifier']
        # TODO What happens with more than one node?
        # TODO Use other information as well?
    else:
        logger.warning("Cannot handle command {}".format(command));

dispatcher.connect(_command_handler, signal=ZIGBEE_AT_RESPONSE) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _stop_handler(sender, **kwargs):
    logger.debug("ZigBee sensor manager stopped")


