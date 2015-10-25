import re
import logging
from pydispatch import dispatcher

__author__ = 'edzard'

logger = logging.getLogger(__name__)

_filters = {}


def _handler(sender, **kwargs):
    global _filters
    for parameter_name in kwargs:
        if parameter_name in _filters:
            data = kwargs[parameter_name]
            if _filters[parameter_name].match(data) is None:
                return
    logger.info("<{}> event from {} -> {}".format(kwargs['signal'], sender, kwargs))

dispatcher.connect(_handler, signal=dispatcher.Any, sender=dispatcher.Any)


def set_filter(**kwargs):
    global _filters
    for parameter_name in kwargs:
        regex = kwargs[parameter_name]
        pattern = re.compile(regex)
        _filters[parameter_name] = pattern