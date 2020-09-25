# -*- coding: utf-8 -*-
"""Utilities for handling csv files

Todo:
    * Write some tests


Created on Nov 27, 2017

@author: croaker
"""


# TODO handle not enough fields, too many fields.
import csv
import logging
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
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
    Type,
)

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass
class RemappedHeader:
    file_field: str
    data_field: str


# TODO replace Any with generics?
# TODO add ability to parse commented csv files, and pull key-value data from comments.
#       maybe make a line pre-reader? what about multi line cells? subclass csv reader?
#       maybe split stream after comments?
class RecordReader(ABC):
    """
    An iterable record reader that translates a line from csv into
    record format of choice.
    """

    def __init__(
        self,
        read_headers_in_first_row: bool = True,
        remapped_headers: Optional[Sequence[RemappedHeader]] = None,
    ):

        self.read_headers_in_first_row = read_headers_in_first_row
        self.remapped_headers = remapped_headers
        self.record_factory: Optional[Callable[[int, Sequence[str]], Any]] = None
        self._headers: Sequence[str] = []

    def _read_record(self, record_num: int, record: Sequence[str]) -> Any:
        if self.record_factory is None:
            raise ValueError("Tried to read a record before record factory set.")
        return self.record_factory(record_num, record)

    def read_records(self, record_stream) -> Generator[Any, None, None]:
        for record_num, record in enumerate(record_stream):
            if record_num == 0:
                self.record_factory = self._init_record_factory(record)
                if self.read_headers_in_first_row:
                    continue
            if self.record_factory is None:
                raise ValueError("Tried to read a record before record factory set.")
            yield self.record_factory(record_num, record)

    @abstractmethod
    def _init_record_factory(self, record) -> Callable[[int, Sequence[str]], Any]:
        raise NotImplementedError

    def headers(self) -> Sequence[str]:

        return tuple(self._headers)

    def _remap_headers(self):
        # if remapped headers are given, use them.
        if self.remapped_headers:
            self._headers = [x.data_field for x in self.remapped_headers]


class RecordWriter(ABC):
    def __init__(
        self,
        record_stream: Iterable[Any],
        remapped_headers: Optional[Sequence[RemappedHeader]] = None,
    ):
        self.enumerated_record_stream = enumerate(record_stream)
        self.remapped_headers = remapped_headers
        self._headers: Sequence[str] = []

        self.record_factory: Optional[Callable[[Sequence[str]], Any]] = None

    def headers(self) -> Sequence[str]:
        return tuple(self._headers)

    def write_records(self) -> Generator[Sequence[str], None, None]:

        for record_num, record in self.enumerated_record_stream:
            if record_num == 0:
                self.record_factory = self._init_record_factory(record)
            if self.record_factory is None:
                raise ValueError("Record factory not initialized")
            yield self.record_factory(record)

    def _remap_headers(self):
        # if remapped headers are given, use them.
        if self.remapped_headers:
            self._headers = [x.file_field for x in self.remapped_headers]

    @abstractmethod
    def _init_record_factory(self, record) -> Callable[[Sequence[str]], Any]:
        raise NotImplementedError


class DictRecordReader(RecordReader):
    def __init__(self, read_headers_in_first_row=True, remapped_headers=None):
        super().__init__(
            read_headers_in_first_row=read_headers_in_first_row,
            remapped_headers=remapped_headers,
        )

    def _init_record_factory(self, record) -> Callable[[int, Sequence[str]], Any]:
        # TODO handle remapped headers
        if self.read_headers_in_first_row:
            self._headers = record
        self._remap_headers()

        def record_factory(line_no, record):
            _ = line_no
            return dict(zip(self._headers, record))

        return record_factory


class DictRecordWriter(RecordWriter):
    def __init__(self, record_stream, remapped_headers=None):
        super().__init__(record_stream, remapped_headers=remapped_headers)

    def _init_record_factory(self, record) -> Callable[[Sequence[str]], Any]:
        # TODO handle remapped headers
        self._headers = record.keys()
        self._remap_headers()

        def record_factory(record):

            return tuple([record[key] for key in record.keys()])

        return record_factory


class NamedTupleRecordReader(RecordReader):
    def __init__(
        self,
        read_headers_in_first_row=True,
        remapped_headers=None,
        record_class_name: str = "Record",
    ):
        self.record_class_name: str = record_class_name

        super().__init__(
            read_headers_in_first_row=read_headers_in_first_row,
            remapped_headers=remapped_headers,
        )

    def _init_record_factory(self, record) -> Callable[[int, Sequence[str]], Any]:
        # TODO handle remapped headers
        if self.read_headers_in_first_row:
            self._headers = record
        self._remap_headers()

        nt_class = namedtuple(self.record_class_name, self._headers)

        def record_factory(line_no, record):
            _ = line_no
            return nt_class(*record)

        return record_factory


class NamedTupleRecordWriter(RecordWriter):
    def __init__(self, record_stream, remapped_headers=None):
        super().__init__(record_stream, remapped_headers=remapped_headers)

    def _init_record_factory(self, record) -> Callable[[Sequence[str]], Any]:
        # TODO handle remapped headers
        self._headers = record._fields
        self._remap_headers()

        def record_factory(record):

            return tuple(record)

        return record_factory


class TupleRecordReader(RecordReader):
    def __init__(self, read_headers_in_first_row=True, remapped_headers=None):
        super().__init__(
            read_headers_in_first_row=read_headers_in_first_row,
            remapped_headers=remapped_headers,
        )

    def _init_record_factory(self, record) -> Callable[[int, Sequence[str]], Any]:
        # TODO handle remapped headers
        if self.read_headers_in_first_row:
            self._headers = record
        self._remap_headers()

        def record_factory(line_no, record):
            _ = line_no
            return tuple(record)

        return record_factory


class TupleRecordWriter(RecordWriter):
    def __init__(
        self,
        record_stream,
        remapped_headers=None,
        headers_in_first_record=True,
    ):
        self.headers_in_first_record = headers_in_first_record
        super().__init__(record_stream, remapped_headers)

    def write_records(self) -> Generator[Sequence[str], None, None]:

        for record_num, record in self.enumerated_record_stream:
            if record_num == 0:
                print(f"in {record_num}")
                if self.headers_in_first_record:
                    print("in header firts record")
                    self.record_factory = self._init_record_factory(record)
                    continue
                else:
                    print("in header not first record")
                    self.record_factory = self._init_record_factory([])
            if self.record_factory is None:
                raise ValueError("Record factory not initialized")
            yield self.record_factory(record)

    def _init_record_factory(self, record) -> Callable[[Sequence[str]], Any]:
        # self._remap_headers()

        self._headers = record
        self._remap_headers()

        def record_factory(record):

            return tuple(record)

        return record_factory


def write_record_to_csv(
    file_path: Path,
    record_writer: Type[RecordWriter],
    header_in_first_line: bool = True,
    parents=False,
    exist_ok=True,
) -> int:
    if parents:
        file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
    with file_path.open("w", encoding="utf8", newline="") as file_out:
        writer = csv.writer(file_out)
        total_count = 0
        for count, item in enumerate(record_writer.write_records()):
            if count == 0:
                if header_in_first_line:
                    writer.writerow(record_writer.headers())
            writer.writerow(item)
            total_count = count
    return total_count + 1


def read_records_from_file(file_path: Path, record_reader: RecordReader):
    data = []
    with file_path.open("r") as file_in:
        csv_reader = csv.reader(file_in)
        data = [x for x in record_reader.read_records(csv_reader)]
    return data


#################################################################################
#
#
#
#
#
#
################################################################################
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


def read_csv_to_row_factory(
    file_in: TextIO,
    row_factory: Callable[[Sequence[str], dict], Any],
    headers_in_first_row: bool = True,
    context: Optional[dict] = None,
) -> Generator[Any, None, None]:
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
