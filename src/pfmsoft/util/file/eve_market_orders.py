from dataclasses import dataclass
from datetime import datetime
from distutils.util import strtobool
from typing import Any, Callable, Dict, Sequence

from pfmsoft.util.file.csv_record import RecordReader, RecordWriter, RemappedHeader


@dataclass
class MarketOrder:
    duration: int
    is_buy_order: bool
    issued: datetime
    location_id: int
    min_volume: int
    order_id: int
    price: float
    range_: str
    system_id: int
    type_id: int
    volume_remain: int
    volume_total: int

    @staticmethod
    def from_strings(string_data: Sequence[str]):
        values: Dict[str, Any] = {
            "duration": int(string_data[0]),
            "is_buy_order": bool(strtobool(string_data[1])),
            "issued": datetime.strptime(string_data[2], "%Y-%m-%dT%H:%M:%SZ"),
            "location_id": int(string_data[3]),
            "min_volume": int(string_data[4]),
            "order_id": int(string_data[5]),
            "price": float(string_data[6]),
            "range_": string_data[7],
            "system_id": int(string_data[8]),
            "type_id": int(string_data[9]),
            "volume_remain": int(string_data[10]),
            "volume_total": int(string_data[11]),
        }
        return MarketOrder(**values)

    def to_string(self):
        str_record = (
            str(self.duration),
            "True" if self.is_buy_order else "False",
            datetime.strftime(self.issued, "%Y-%m-%dT%H:%M:%SZ"),
            str(self.location_id),
            str(self.min_volume),
            str(self.order_id),
            str(self.price),
            str(self.range_),
            str(self.system_id),
            str(self.type_id),
            str(self.volume_remain),
            str(self.volume_total),
        )
        return str_record


def make_remapped_headers():
    file_headers = [
        "duration",
        "is_buy_order",
        "issued",
        "location_id",
        "min_volume",
        "order_id",
        "price",
        "range",
        "system_id",
        "type_id",
        "volume_remain",
        "volume_total",
    ]
    object_headers = [
        "duration",
        "is_buy_order",
        "issued",
        "location_id",
        "min_volume",
        "order_id",
        "price",
        "range_",
        "system_id",
        "type_id",
        "volume_remain",
        "volume_total",
    ]
    return [RemappedHeader(*x) for x in zip(file_headers, object_headers)]


class MarketOrderRecordReader(RecordReader):
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

            return MarketOrder.from_strings(record)

        return record_factory


class MarketOrderRecordWriter(RecordWriter):
    def __init__(self, record_stream, remapped_headers=None):
        super().__init__(record_stream, remapped_headers=remapped_headers)

    def _init_record_factory(self, record) -> Callable[[Sequence[str]], Any]:
        # TODO handle remapped headers

        self._remap_headers()

        def record_factory(record):

            return tuple(record.to_string())

        return record_factory
