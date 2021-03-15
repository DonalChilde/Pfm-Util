import logging
from typing import Any, Callable

# TODO need docs!
__VERSION__ = "0.1.0"

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def simple_filter(desired_value: Any) -> Callable[[Any], bool]:
    """A simple filter function factory, compares using ==

    :param desired_value: value to be compared against.
    :returns: The filter function
    """
    logger.debug("Creating simple filter for value: %s", desired_value)

    def filter_function(value: Any) -> bool:
        """A simple filter function that will compare a value with a previously
            defined desired value.

        :param value: value to compare
        :returns: True for match
        """
        if value == desired_value:
            return True
        return False

    return filter_function
