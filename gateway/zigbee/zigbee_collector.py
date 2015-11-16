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

logger = zigbee.logger

# TODO Can we get signal strength?


class Collector:

    _port = None
    _xbee = None

    def __init__(self, serial_port="/dev/tty/tty.usbserial", baud_rate=9600):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        dispatcher.connect(self._start_handler, signal=START_SIGNAL, sender='gateway')

    # Callback for the xbee library
    def _frame_handler(self, frame):
        logger.debug("Received zigbee frame {}".format(frame))
        # Timestamp it
        timestamp = datetime.now()  # TODO Add timezone support
        # Send appropriate event
        type_switch= {
            'rx': ZIGBEE_RX,
            'rx_io_data_long_addr': ZIGBEE_RX_IO_DATA_LONG_ADDR,
            'at_response': ZIGBEE_AT_RESPONSE
        }
        signal = type_switch.get(frame['id'], None)
        if signal is not None:
            dispatcher.send(signal=signal, sender=self, timestamp=timestamp, frame=frame)
        else:
            logger.warning("{} does not know how to deal with {} frames".format(__name__, frame['id']))

    def trigger_network_discovery(self):
        # TODO: also get local info?
        _xbee.send('at', frame_id=b'A', command=b'ND') # TODO find out what the frame id is for
        logger.debug("Sent ND (node discover) command")

    def _start_handler(self):
        global _port, _xbee
        try:
            # Hook-up ZigBee modem
            _port = serial.Serial(self.serial_port, self.baud_rate)
            _xbee = ZigBee(_port, callback=self._frame_handler)
            # Finished
            dispatcher.connect(self._stop_handler, signal=STOP_SIGNAL, sender='gateway')
            logger.debug("started")
        except SerialException as sex:
            logger.error(sex.strerror)  # Serial port not found?

    def _stop_handler(self):
        _xbee.halt()
        _port.close()
        logger.debug("stopped")
