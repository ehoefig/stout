import serial
from datetime import datetime
from gateway import START_SIGNAL, STOP_SIGNAL, zigbee
from pydispatch import dispatcher
from xbee import ZigBee
from serial.serialutil import SerialException

__author__ = 'edzard'

ZIGBEE_RX = 'zigbee_rx'
ZIGBEE_RX_IO_DATA_LONG_ADDR = 'zigbee_rx_io_data_long_addr'
ZIGBEE_AT_RESPONSE = 'zigbee_at_response'

_port = None
_xbee = None

serial_port = "/dev/tty/tty.usbserial"
baud_rate = 9600
logger = zigbee.logger

# TODO Can we get signal strength?


# Callback for the xbee library
def _frame_handler(frame):
    # Timestamp it
    timestamp = datetime.now()  # TODO Add timezone support
    # Send appropriate event
    type_switch= {
        'rx' : ZIGBEE_RX,
        'rx_io_data_long_addr': ZIGBEE_RX_IO_DATA_LONG_ADDR,
        'at_response': ZIGBEE_AT_RESPONSE
    }
    signal = type_switch.get(frame['id'], None)
    if signal is not None:
        dispatcher.send(signal=signal, sender=__name__, timestamp=timestamp, frame=frame)
    else:
        logger.warning("{} does not know how to deal with {} frames".format(__name__, frame['id']))
    logger.debug("Received zigbee frame {}".format(frame))


def trigger_network_discovery():
    # TODO: also get local info?
    _xbee.send('at', frame_id=b'A', command=b'ND') # TODO find out what the frame id is for
    logger.debug("Sent ND (network discovery) command")

def _start_handler(sender, **kwargs):
    global _port, _xbee
    try:
        # Hook-up ZigBee modem
        _port = serial.Serial(serial_port, baud_rate)
        _xbee = ZigBee(_port, callback=_frame_handler)
        # Finished
        dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
        logger.debug("Zigbee collector started")
    except SerialException as sex:
        logger.error(sex.strerror)  # Serial port not found?

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _stop_handler(sender, **kwargs):
    _xbee.halt()
    _port.close()
    logger.debug("ZigBee collector stopped")


