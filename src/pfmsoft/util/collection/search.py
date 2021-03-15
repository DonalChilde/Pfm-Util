import logging
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TypeVar

from pfmsoft.util.collection.misc import wrap_range

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

T = TypeVar("T")


def search_list_of_dicts(
    data: List[Dict[Any, Any]],
    search_key,
    search_value,
    target_key,
    target_default_value,
):
    # returns target default value if unable to match search_key and or value_key
    # TODO convert to itemgetter etc.
    for item in data:
        if search_key in item:
            if item[search_key] == search_value:
                return item.get(target_key, target_default_value)
    return target_default_value


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
