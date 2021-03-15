"""Utilities for handling csv files

Todo:
    * Write some tests


Created on Nov 27, 2017

@author: croaker
"""


# TODO handle not enough fields, too many fields.
import csv
import logging
from collections import namedtuple
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    NamedTuple,
    Optional,
    Sequence,
    TextIO,
)

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def write_list_of_dicts_to_csv(
    data: Sequence[Dict[str, Any]],
    file_path: Path,
    mode: str = "w",
    parents: bool = True,
    exist_ok: bool = True,
    field_names: Optional[Sequence[str]] = None,
) -> int:
    """
    Save a list of dicts to csv. Makes parent directories if they don't exist.

    :param data: Data to save.
    :param file_path: Path to saved file. Existing files will be overwritten.
    :param mode: File mode to use. As used in `open`. Limited to 'w' or 'x'. Defaults to 'w'.
    :param parents: Make parent directories if they don't exist. As used by `Path.mkdir`, by default True
    :param exist_ok: Suppress exception if parent directory exists as directory. As used by `Path.mkdir`, by default True
    :param field_names: Optionally reorder fields, by default None
    :return: records writen.
    :raises Exception: Any exception that can be raised from Path.mkdir or Path.open
    """
    # TODO rewrite to handle list of objects, see collection.sort.index_objects
    #   this would need a list of fields, so make helpers list of dicts etc?
    try:
        if mode not in ["w", "x"]:
            raise ValueError(f"Unsupported file mode '{mode}'.")
        if parents:
            file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
        if field_names is None:
            field_names = list(data[0].keys())
        with file_path.open(mode, encoding="utf8", newline="") as file_out:
            writer = csv.DictWriter(file_out, fieldnames=field_names)
            writer.writeheader()
            total_count = 0
            for count, item in enumerate(data):
                writer.writerow(item)
                total_count = count
        return total_count + 1
    except Exception as error:
        logger.exception("Error trying to save data to %s", file_path, exc_info=True)
        raise error


def write_named_tuple_to_csv(
    data: Sequence[NamedTuple],
    file_path: Path,
    mode: str = "w",
    parents: bool = True,
    exist_ok: bool = True,
) -> int:
    try:
        if mode not in ["w", "x"]:
            raise ValueError(f"Unsupported file mode '{mode}'.")
        if parents:
            file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
        with file_path.open(mode, encoding="utf8", newline="") as file_out:
            writer = csv.writer(file_out)
            writer.writerow(data[0]._fields)
            total_count = 0
            for count, item in enumerate(data):
                writer.writerow(item)
                total_count = count
        return total_count + 1
    except Exception as error:
        logger.exception("Error trying to save data to %s", file_path, exc_info=True)
        raise error


def write_list_to_csv(
    data: Iterable[Sequence],
    file_path: Path,
    mode: str = "w",
    parents: bool = True,
    exist_ok: bool = True,
    has_header: bool = True,
    headers: Optional[Sequence[str]] = None,
) -> int:
    """
    Writes an iterator of lists to a file in csv format.

    :param data: [description]
    :param file_path: [description]
    :param mode: File mode to use. As used in `open`. Limited to 'w' or 'x'. Defaults to 'w'.
    :param parents: [description], by default True
    :param exist_ok: [description], by default True
    :param has_header: First row of supplied data is the header, by default True
    :param headers: Headers to use if not supplied in data, by default None
    :returns: Number of rows saved, not including a header
    :raises ValueError: Number of items in a row does not match number of headers.
    """
    # TODO how does this handle missing fields and excess fields?
    try:
        if mode not in ["w", "x"]:
            raise ValueError(f"Unsupported file mode '{mode}'.")
        if parents:
            file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
        with file_path.open(mode, encoding="utf8", newline="") as file_out:
            writer = csv.writer(file_out)
            iterable_data = iter(data)

            if has_header:
                header_row = next(iterable_data)
                writer.writerow(header_row)
            else:
                if headers is not None:
                    header_row = headers
                    writer.writerow(header_row)
                else:
                    header_row = []
            total_count = 0
            for count, item in enumerate(iterable_data):
                if count > 0 and has_header:
                    if len(header_row) > 0 and len(header_row) != len(item):
                        raise ValueError(
                            f"Header has {len(header_row)} but row has {len(item)} items"
                        )
                    writer.writerow(item)
                    total_count = count
        return total_count + 1
    except Exception as error:
        logger.exception("Error trying to save data to %s", file_path, exc_info=True)
        raise error


# TODO this code can be easily extended to support reading and
#   writing arbitrary objects through factories.


def read_csv_to_row_factory(
    file_in: TextIO,
    row_factory: Callable[[Sequence[str], dict], Any],
    headers_in_first_row: bool = True,
    context: Optional[dict] = None,
) -> Generator[Any, None, None]:
    # TODO change context to header or header_override
    if context is None:
        context = {}
    reader = csv.reader(file_in)
    if headers_in_first_row:
        headers = next(reader)
    else:
        headers = []
    factory = row_factory(headers, context)
    return (factory(*row) for row in reader)


def named_tuple_factory(headers, context):
    header_override = context.get("header_override", None)
    if header_override is not None:
        headers = header_override

    n_tuple = namedtuple("CsvRow", headers)

    def factory(row):
        if len(headers) != len(row):
            raise ValueError(f"Header has {len(headers)} but row has {len(row)} items")
        return n_tuple(*row)

    return factory


def tuple_factory(_headers, _context):
    def factory(row):
        return tuple(row)

    return factory


def dict_factory(headers, context):
    header_override = context.get("header_override", None)
    if header_override is not None:
        headers = header_override

    def factory(row):
        if len(headers) != len(row):
            raise ValueError(f"Header has {len(headers)} but row has {len(row)} items")
        return dict(zip(headers, row))

    return factory


# def read_csv_to_named_tuple(
#     file_in, use_header_row: bool, field_names: Optional[Sequence[str]] = None
# ):
#     if field_names is None:
#         field_names = []
#     reader = csv.reader(file_in)
#     if use_header_row:
#         field_names = next(reader)
#     CsvRow = namedtuple("CsvRow", field_names)
#     return (CsvRow(*row) for row in reader)
