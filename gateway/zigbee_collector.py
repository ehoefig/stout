import logging
import serial
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


def frame_handler(frame):
    dispatcher.send(ZIGBEE_FRAME_SIGNAL, __name__, frame=frame)
    logger.debug(frame)


def start_handler(sender, **kwargs):
    global _port, _xbee
    try:
        _port = serial.Serial(serial_port, baud_rate)
        _xbee = ZigBee(_port, callback=frame_handler)
        dispatcher.connect(stop_handler, signal=STOP_SIGNAL, sender=dispatcher.Any)
        logger.debug("started")
    except SerialException as sex:
        logger.error(sex.strerror)


dispatcher.connect(start_handler, signal=START_SIGNAL, sender=dispatcher.Any)

def stop_handler(sender, **kwargs):
    _xbee.halt()
    _port.close()
    logger.debug("stopped.")


