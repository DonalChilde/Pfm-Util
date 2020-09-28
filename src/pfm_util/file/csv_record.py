"""
This is an effort to make csv support for arbitrary objects.
This might be handled better through factory functions and the
regular csv util library.

"""
import csv
import logging
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generator, Iterable, Optional, Sequence, Type

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
        self, record_stream, remapped_headers=None, headers_in_first_record=True
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
