from pydispatch import dispatcher
from datetime import timedelta
import gateway
from gateway import START_SIGNAL, STOP_SIGNAL, zigbee
from gateway.zigbee import ZigBeeAddress, ZigBeeSensor
from gateway.zigbee.zigbee_collector import ZIGBEE_RX_IO_DATA_LONG_ADDR, ZIGBEE_AT_RESPONSE, ZIGBEE_RX, trigger_network_discovery
from gateway.network import NEW_DATA_SIGNAL, add_sensor, get_sensor, has_sensor_for_address

__author__ = 'edzard'

logger = zigbee.logger

map = {}


def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    logger.debug("ZigBee sensor manager started")

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _get_sensor_from_frame_data(params):

    address = ZigBeeAddress(params['source_addr_long'], params['source_addr'])
    if has_sensor_for_address(address):
        # Already know that one!
        sensor = get_sensor(address)
    else:

        # Check if type is given by configuration mapping
        if address.as_hex() in map:
            # Create specific sensor type
            sensor_class = map[address.as_hex()]
            sensor = sensor_class(address)
        else:
            # Choose generic ZigBee sensor
            sensor = ZigBeeSensor(address)

        add_sensor(sensor)
        logger.debug("{} with address {} created".format(type(sensor).__name__, address))

        # Try to set initial location
        if gateway.location is not None:
            sensor.location = gateway.location

        # Try to get some more infos (e.g. name)
        # TODO Trigger ND based on timer? (At least wait until a pending ND is answered)
        trigger_network_discovery()

    return sensor


def _rx_data_handler(sender, **kwargs):
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    sensor = _get_sensor_from_frame_data(frame)
    data = frame['rf_data']
    num_samples = sensor.get_num_samples_per_frame()
    sample_size = len(data) // num_samples
    # TODO FEATURE normalize timesteamps in a sensor-independent way?
    sample_time_delta = timedelta(microseconds=1000000/sensor.get_sampling_frequency())
    timestamp -= (num_samples-1) * sample_time_delta
    for i in range(0, num_samples):
        orientation, linear_acceleration = sensor.convert(data[i*sample_size:i*sample_size+sample_size])
        dispatcher.send(signal=NEW_DATA_SIGNAL, sender=__name__, sensor=sensor, timestamp=timestamp,
                        orientation=orientation, linear_acceleration=linear_acceleration)
        timestamp += sample_time_delta

dispatcher.connect(_rx_data_handler, signal=ZIGBEE_RX) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _io_sample_handler(sender, **kwargs):
    frame = kwargs['frame']
    timestamp = kwargs['timestamp']
    sensor = _get_sensor_from_frame_data(frame)
    for sample_tuple in frame['samples']:
        acceleration = sensor.convert(sample_tuple)
        # TODO adjust timestamp for multiple samples
        dispatcher.send(signal=NEW_DATA_SIGNAL, sender=__name__, sensor=sensor, timestamp=timestamp, acceleration=acceleration)

dispatcher.connect(_io_sample_handler, signal=ZIGBEE_RX_IO_DATA_LONG_ADDR) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _command_handler(sender, **kwargs):
    frame = kwargs['frame']
    command = frame['command'].decode()
    failure = frame['status'] == b'\x01'
    if failure:
        logger.warning("{} command failed".format(command))
    else:
        if command == 'ND':
            parameter = frame['parameter']
            sensor = _get_sensor_from_frame_data(parameter)
            sensor.name = parameter['node_identifier'].decode()
            # TODO What happens with more than one node?
            # TODO Use other information as well?
        else:
            logger.warning("Cannot handle command {}".format(command));

dispatcher.connect(_command_handler, signal=ZIGBEE_AT_RESPONSE) # TODO Why does this parameter not work? -> sender='gateway.zigbee_collector'


def _stop_handler(sender, **kwargs):
    logger.debug("ZigBee sensor manager stopped")


