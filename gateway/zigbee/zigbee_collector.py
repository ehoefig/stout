import logging
import serial
from datetime import datetime
from gateway import START_SIGNAL
from gateway import STOP_SIGNAL
from pydispatch import dispatcher
from xbee import ZigBee
from serial.serialutil import SerialException

__author__ = 'edzard'

ZIGBEE_RX_IO_DATA_LONG_ADDR = 'zigbee_rx_io_data_long_addr'
ZIGBEE_AT_RESPONSE = 'zigbee_at_response'

_port = None
_xbee = None

serial_port = "/dev/tty/tty.usbserial"
baud_rate = 9600
logger = logging.getLogger(__name__)


# Callback for the xbee library
def _frame_handler(frame):
    # Timestamp it
    timestamp = datetime.now()  # TODO Add timezone support
    # Send appropriate event
    type_switch= {
        'rx_io_data_long_addr': ZIGBEE_RX_IO_DATA_LONG_ADDR,
        'at_response': ZIGBEE_AT_RESPONSE
    }
    signal = type_switch.get(frame['id'], None)
    if signal is not None:
        dispatcher.send(signal=signal, sender=__name__, timestamp=timestamp, frame=frame)
    else:
        logger.warning("{} does not know how to deal with {} frames".format(__name__, frame['id']))
    logger.debug("Received zigbee frame {}".format(frame))


def _start_handler(sender, **kwargs):
    global _port, _xbee
    try:
        # Hook-up ZigBee modem
        _port = serial.Serial(serial_port, baud_rate)
        _xbee = ZigBee(_port, callback=_frame_handler)

         # Network Discovery
        # TODO: integrate somewhere else?
        # TODO: also get local info?
        _xbee.send('at', frame_id=b'A', command=b'ND')
        logger.debug("Sent ND (network discovery) command")

        # Finished
        dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
        logger.debug("started")
    except SerialException as sex:
        logger.error(sex.strerror)  # Serial port not found?

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _stop_handler(sender, **kwargs):
    _xbee.halt()
    _port.close()
    logger.debug("stopped.")


