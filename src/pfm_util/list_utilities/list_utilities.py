import logging
from itertools import chain, islice, repeat
from typing import Any, Callable, Iterator, Optional, Sequence, Tuple

# TODO need docs!
__VERSION__ = "0.1.0"

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


# TODO keep these as examples, suggest use more itertools
def chunk(it, size):
    """
    https://stackoverflow.com/a/22045226
    """
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def chunk_pad(it, size, padval=None):
    """
    https://stackoverflow.com/a/22045226
    """
    it = chain(iter(it), repeat(padval))
    return iter(lambda: tuple(islice(it, size)), (padval,) * size)


def chunks(l, n):
    """
    https://stackoverflow.com/a/1751478
    """
    n = max(1, n)
    return (l[i : i + n] for i in range(0, len(l), n))


def wrap_range(
    left_bound: int, right_bound: int, start_index: int, direction: int
) -> Iterator[int]:
    """Create a range of integer values that start somewhere between the beginning and end, wrapping around back to start.

    e.g. wrap_range(0,10,6,1) = [6, 7, 8, 9, 0, 1, 2, 3, 4, 5]
         wrap_range(0,10,6,-1) = [6, 5, 4, 3, 2, 1, 0, 9, 8, 7]
         wrap_range(-2, 10, 6, -1) = [6, 5, 4, 3, 2, 1, 0, -1, -2, 9, 8, 7]

    note right_bound mimics the behavior of range(),
    where range(0,10) = [0,1,2,3,4,5,6,7,8,9]

    :param left_bound: lower boundry of number line
    :param right_bound: upper boundry of number line + 1
    :param start_index: starting value, must be  left_bound >= start_index < right_bound
    :param direction: a positive or negative integer, where positive integers increment
        to the right on the number line, and negative integers increment to the left.
    :raises ValueError: direction cannot be zero
    :raises ValueError: left_bound cannot be greater than right_bound
    :returns: Two range() generators chained by itertools.chain
    """
    logger.debug(
        "wrap_range(left_bound=%s, right_bound=%s, start_index=%s, direction=%s)",
        left_bound,
        right_bound,
        start_index,
        direction,
    )
    if direction == 0:
        raise ValueError("direction cannot be zero")
    if left_bound > right_bound:
        raise ValueError(
            f"left_bound {left_bound} is greater than right_bound {right_bound}"
        )
    range_generator = None
    if direction > 0:
        left_range = range(left_bound, start_index)
        right_range = range(start_index, right_bound)
        range_generator = chain(right_range, left_range)
    else:
        left_range = range(start_index, left_bound - 1, -1)
        right_range = range(right_bound - 1, start_index, -1)
        range_generator = chain(left_range, right_range)
    return range_generator


def distance_in_list(
    list_data: Sequence[Any],
    start_index: int,
    direction: int,
    filter_function: Callable[[Any], bool],
) -> Tuple[Optional[int], Optional[int]]:
    """Find the distance between a starting index, and the first matching object in a list. Search will wrap around the list.

    :param list_data: Sequence to search
    :param start_index: Index to start from
    :param direction: A positive integer to start search to the right, negative for left. Zero is not allowed.
    :param filter_function: The filter function to define a match.
    :returns: (distance,index_of_match) or (None,None) if no match found.
    """
    logging.debug(
        "distance_in_list(list_data=%s, start_index=%s, direction=%s, filter_function=%s)",
        list_data,
        start_index,
        direction,
        filter_function,
    )
    logging.debug(
        "range_generator as list=%s",
        list(wrap_range(0, len(list_data), start_index, direction)),
    )
    range_generator = wrap_range(0, len(list_data), start_index, direction)
    for distance, index in enumerate(range_generator):
        if filter_function(list_data[index]):
            return (distance, index)
    return (None, None)


def simple_filter(desired_value: Any) -> Callable[[Any], bool]:
    """A simple filter function factory, compares using ==

    :param desired_value: value to be compared against.
    :returns: The filter function
    """
    logger.debug("Creating simple filter for value: %s", desired_value)

    def filter_function(value: Any) -> bool:
        """A simple filter function that will compare a value with a previously defined desired value

        :param value: value to compare
        :returns: True for match
        """
        if value == desired_value:
            return True
        return False

    return filter_function
