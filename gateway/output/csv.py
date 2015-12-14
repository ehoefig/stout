import logging
from gateway import START_SIGNAL, STOP_SIGNAL, NEW_DATA_SIGNAL
from pydispatch import dispatcher

__author__ = 'edzard'

logger = logging.getLogger(__name__)
path = None

_file = None
_separator = ';'

def _start_handler():
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    global _file
    _file = open(path, 'a', encoding='utf-8')
    logger.debug("CSV output handler appending to {}".format(_file.name))

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _data_handler(sender, timestamp, orientation, linear_acceleration):
    str = "{};{};{};{};{};{};{};{}".format(
        timestamp,
        linear_acceleration['x'], linear_acceleration['y'], linear_acceleration['z'],
        orientation['w'], orientation['x'], orientation['y'], orientation['z'])
    str = str.replace('.',',')
    logger.debug("Writing data: \"{}\"".format(str))
    _file.write(str + '\n')

dispatcher.connect(_data_handler, signal=NEW_DATA_SIGNAL)


def _stop_handler():
    # TODO: Graceful disconnect: finish writes before closing file
    _file.close()
    logger.debug("CSV output handler finished appending to {}".format(_file.name))

