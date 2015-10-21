import logging
import serial
from datetime import datetime
from gateway import START_SIGNAL
from gateway import STOP_SIGNAL
from pydispatch import dispatcher
from xbee import ZigBee
from serial.serialutil import SerialException

__author__ = 'edzard'

ZIGBEE_FRAME_SIGNAL = 'new_zigbee_frame'

_port = None
_xbee = None

serial_port = "/dev/tty/tty.usbserial"
baud_rate = 9600
logger = logging.getLogger(__name__)


# Callback for the xbee library
def _frame_handler(frame):
    timestamp = datetime.now()  # TODO Add timezone support
    dispatcher.send(signal=ZIGBEE_FRAME_SIGNAL, sender=__name__, timestamp=timestamp, frame=frame)
    logger.debug(frame)


def _start_handler(sender, **kwargs):
    global _port, _xbee
    try:
        _port = serial.Serial(serial_port, baud_rate)
        _xbee = ZigBee(_port, callback=_frame_handler)
        dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
        logger.debug("started")
    except SerialException as sex:
        logger.error(sex.strerror)

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _stop_handler(sender, **kwargs):
    _xbee.halt()
    _port.close()
    logger.debug("stopped.")


