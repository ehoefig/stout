import logging
from gateway import START_SIGNAL, STOP_SIGNAL
from pydispatch import dispatcher
from apscheduler.schedulers.background import BackgroundScheduler

__author__ = 'edzard'

TIMER_SIGNAL = 'timer'

_scheduler = BackgroundScheduler()

logger = logging.getLogger(__name__)

logging.getLogger('apscheduler').parent = logger


def _start_handler(sender, **kwargs):
    dispatcher.connect(_stop_handler, signal=STOP_SIGNAL, sender='gateway')
    _scheduler.add_job(_timer_up, 'interval', seconds=1)
    _scheduler.start()
    logger.debug("Timer started")

dispatcher.connect(_start_handler, signal=START_SIGNAL, sender='gateway')


def _timer_up():
    dispatcher.send(TIMER_SIGNAL, __name__)


def _stop_handler(sender, **kwargs):
    _scheduler.shutdown()
    logger.debug("Timer stopped")

