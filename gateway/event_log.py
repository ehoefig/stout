import re
import logging
from pydispatch import dispatcher

__author__ = 'edzard'

logger = logging.getLogger(__name__)

_filters = {}


def _handler(sender, **kwargs):
    global _filters
    raw_data = repr(kwargs)
    overall_match = True
    for parameter_name in _filters:
        if not parameter_name in kwargs or _filters[parameter_name].match(raw_data) is None:
            overall_match = False
    if overall_match:
        logger.info("<{}> event from {} -> {}".format(kwargs['signal'], sender, raw_data))

dispatcher.connect(_handler, signal=dispatcher.Any, sender=dispatcher.Any)


def set_filter(**kwargs):
    global _filters
    for parameter_name in kwargs:
        regex = kwargs[parameter_name]
        pattern = re.compile(regex)
        _filters[parameter_name] = pattern