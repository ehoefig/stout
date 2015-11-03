from pydispatch import dispatcher
import gateway
from gateway import START_SIGNAL, STOP_SIGNAL, zigbee
from gateway.zigbee import ZigBeeAddress, ZigBeeBaseSensor
from gateway.zigbee.zigbee_collector import ZIGBEE_RX_IO_DATA_LONG_ADDR, ZIGBEE_AT_RESPONSE, ZIGBEE_RX, trigger_network_discovery
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
        # Do we know the type?
        if address.as_hex() in map:
            # Create a new one
            sensor_class = map[address.as_hex()]
            sensor = sensor_class(address)
            add_sensor(sensor)
            logger.debug("{} sensor with address {} created".format(type(sensor).__name__, address))
        # Try to set initial location
        if gateway.location is not None:
            sensor.location = gateway.location
        # Try to get some more infos (e.g. name)
        trigger_network_discovery()
    return sensor


def _rx_data_handler(sender, **kwargs):
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    sensor = _identify_source_address(frame)
    data = frame['rf_data']
    # TODO: use sensor objects to map data to python
    logger.info("Data: {}".format(data))
    for i in range(0, 5):
        # dispatch 5 separate samples
        # dispatcher.send(signal=NEW_DATA_SIGNAL, sender=__name__, sensor=sensor, timestamp=timestamp, acceleration=data)
        pass

dispatcher.connect(_rx_data_handler, signal=ZIGBEE_RX) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _io_sample_handler(sender, **kwargs):
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    sensor = _identify_source_address(frame)
    for sample_tuple in frame['samples']:
        # TODO use sensor map to access sensor data
        data = {'x': sample_tuple['adc-0'], 'y': sample_tuple['adc-1'], 'z': sample_tuple['adc-2']}
        dispatcher.send(signal=NEW_DATA_SIGNAL, sender=__name__, sensor=sensor, timestamp=timestamp, acceleration=data)

dispatcher.connect(_io_sample_handler, signal=ZIGBEE_RX_IO_DATA_LONG_ADDR) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _command_handler(sender, **kwargs):
    frame = kwargs['frame']
    command = frame['command'].decode()
    if command == 'ND':
        parameter = frame['parameter']
        sensor = _identify_source_address(parameter)
        sensor.name = parameter['node_identifier'].decode()
        # TODO What happens with more than one node?
        # TODO Use other information as well?
    else:
        logger.warning("Cannot handle command {}".format(command));

dispatcher.connect(_command_handler, signal=ZIGBEE_AT_RESPONSE) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _stop_handler(sender, **kwargs):
    logger.debug("ZigBee sensor manager stopped")


