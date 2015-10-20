import logging
from pydispatch import dispatcher

__author__ = 'edzard'

logger = logging.getLogger(__name__)


def handler(sender, **kwargs):
    logger.debug("<{}> event from {} -> {}".format(kwargs['signal'], sender, kwargs))

dispatcher.connect(handler, signal=dispatcher.Any, sender=dispatcher.Any)
