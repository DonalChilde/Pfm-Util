# from pathlib import Path
# from pprint import PrettyPrinter

# import pytest

# from utility_lib.file_utilities.csv_utililities import (
#     DictRecordReader,
#     DictRecordWriter,
#     NamedTupleRecordReader,
#     NamedTupleRecordWriter,
#     RecordReader,
#     RecordWriter,
#     RemappedHeader,
#     TupleRecordReader,
#     TupleRecordWriter,
#     read_records_from_file,
#     write_list_to_csv,
#     write_record_to_csv,
# )
# from utility_lib.file_utilities.eve_market_orders import (
#     MarketOrderRecordReader,
#     MarketOrderRecordWriter,
#     make_remapped_headers,
# )

# pp = PrettyPrinter(width=180)


# @pytest.fixture(scope="function")
# def csv_test_data(tmp_path):

#     test_data_output_root_dir = tmp_path / "csv_test_output"
#     test_data_output_root_dir.mkdir(exist_ok=True)
#     data = {
#         "output_root_dir": test_data_output_root_dir,
#         "test_data_list_of_tuple_str": test_data_list_of_tuple_str(),
#         "sample_csv_path": Path(__file__).parent
#         / "test_data/market_orders_10000033.49_of_49.csv",
#     }
#     return data


# def test_read_tuple_data(csv_test_data):
#     record_reader = TupleRecordReader()
#     data = read_records_from_file(csv_test_data["sample_csv_path"], record_reader)
#     assert len(data) == 400
#     pp.pprint(record_reader.headers())
#     pp.pprint(data[:10])
#     # assert False


# def test_read_MarketOrder_data(csv_test_data):
#     record_reader = MarketOrderRecordReader()
#     data = read_records_from_file(csv_test_data["sample_csv_path"], record_reader)
#     assert len(data) == 400
#     pp.pprint(record_reader.headers())
#     pp.pprint(data[:10])
#     # assert False


# def test_read_write_MarketOrder_data(csv_test_data):
#     record_reader = MarketOrderRecordReader()
#     data = read_records_from_file(csv_test_data["sample_csv_path"], record_reader)

#     assert len(data) == 400
#     file_path = csv_test_data["output_root_dir"] / "csv_from_MarketOrder.csv"
#     remapped_headers = make_remapped_headers()
#     record_writer = MarketOrderRecordWriter(data, remapped_headers=remapped_headers)
#     write_record_to_csv(file_path, record_writer)
#     new_data = read_records_from_file(file_path, record_reader)
#     assert data == new_data

#     nt_reader = NamedTupleRecordReader()
#     original_data = read_records_from_file(csv_test_data["sample_csv_path"], nt_reader)
#     market_order_data = read_records_from_file(file_path, nt_reader)
#     assert original_data == market_order_data


# def test_read_dict_data(csv_test_data):
#     record_reader = DictRecordReader()
#     data = read_records_from_file(csv_test_data["sample_csv_path"], record_reader)
#     assert len(data) == 400
#     pp.pprint(record_reader.headers())
#     pp.pprint(data[:10])
#     # assert False


# def test_read_write_dict_data(csv_test_data):
#     record_reader = DictRecordReader()
#     data = read_records_from_file(csv_test_data["sample_csv_path"], record_reader)
#     assert len(data) == 400
#     file_path = csv_test_data["output_root_dir"] / "csv_from_dict.csv"
#     record_writer = DictRecordWriter(data)
#     write_record_to_csv(file_path, record_writer)
#     new_data = read_records_from_file(file_path, record_reader)
#     assert data == new_data


# def test_read_namedtuple_data(csv_test_data):
#     record_reader = NamedTupleRecordReader()
#     data = read_records_from_file(csv_test_data["sample_csv_path"], record_reader)
#     assert len(data) == 400
#     pp.pprint(record_reader.headers())
#     pp.pprint(data[:10])
#     # assert False


# def test_read_write_namedtuple_data(csv_test_data):
#     record_reader = NamedTupleRecordReader()
#     data = read_records_from_file(csv_test_data["sample_csv_path"], record_reader)
#     assert len(data) == 400
#     file_path = csv_test_data["output_root_dir"] / "csv_from_namedtuple.csv"
#     record_writer = NamedTupleRecordWriter(data)
#     write_record_to_csv(file_path, record_writer)
#     new_data = read_records_from_file(file_path, record_reader)
#     assert data == new_data


# def test_write_tuple_data(csv_test_data):
#     file_path = csv_test_data["output_root_dir"] / "csv_from_lists.csv"
#     record_writer = TupleRecordWriter(csv_test_data["test_data_list_of_tuple_str"])
#     count = write_record_to_csv(file_path, record_writer)
#     print(file_path)
#     assert count == 12


# def test_write_read_tuple_data(csv_test_data):
#     file_path = csv_test_data["output_root_dir"] / "csv_from_tuple.csv"
#     record_writer = TupleRecordWriter(csv_test_data["test_data_list_of_tuple_str"])
#     count = write_record_to_csv(file_path, record_writer)
#     assert record_writer.headers() == csv_test_data["test_data_list_of_tuple_str"][0]
#     print(file_path)
#     assert count == 12
#     record_reader = TupleRecordReader()
#     records = read_records_from_file(file_path, record_reader)

#     records.insert(0, tuple(record_reader.headers()))
#     pp.pprint(records)
#     assert records == csv_test_data["test_data_list_of_tuple_str"]
#     # assert False


# def test_lists_to_csv(csv_test_data):
#     file_path = csv_test_data["output_root_dir"] / "csv_from_lists.csv"
#     count = write_list_to_csv(csv_test_data["test_data_list_of_tuple_str"], file_path)
#     print(file_path)
#     assert count == 12


# def test_data_list_of_tuple_str():
#     data = [
#         (
#             "duration",
#             "is_buy_order",
#             "issued",
#             "location_id",
#             "min_volume",
#             "order_id",
#             "price",
#             "range",
#             "system_id",
#             "type_id",
#             "volume_remain",
#             "volume_total",
#         ),
#         (
#             "90",
#             "True",
#             "2019-12-01T10:49:59Z",
#             "60004099",
#             "1",
#             "5554953115",
#             "1.0",
#             "region",
#             "30002779",
#             "14021",
#             "1000",
#             "1000",
#         ),
#         (
#             "90",
#             "True",
#             "2019-12-12T14:57:22Z",
#             "60004327",
#             "1",
#             "5562948518",
#             "0.03",
#             "40",
#             "30002751",
#             "266",
#             "1000",
#             "1000",
#         ),
#         (
#             "90",
#             "True",
#             "2019-12-12T14:56:36Z",
#             "1025026043977",
#             "1",
#             "5541845956",
#             "2500013.97",
#             "5",
#             "30002782",
#             "25625",
#             "10",
#             "20",
#         ),
#         (
#             "90",
#             "True",
#             "2019-11-09T23:08:53Z",
#             "1025026043977",
#             "1",
#             "5489155023",
#             "900.15",
#             "region",
#             "30002782",
#             "28367",
#             "12000",
#             "12000",
#         ),
#         (
#             "90",
#             "True",
#             "2019-10-02T17:25:33Z",
#             "60004099",
#             "1",
#             "5516155873",
#             "1.0",
#             "region",
#             "30002779",
#             "33101",
#             "995",
#             "1000",
#         ),
#         (
#             "90",
#             "True",
#             "2019-12-05T13:55:30Z",
#             "60015008",
#             "1",
#             "5520663950",
#             "4.36",
#             "1",
#             "30041392",
#             "34",
#             "3495793",
#             "60000000",
#         ),
#         (
#             "90",
#             "True",
#             "2019-12-08T19:13:08Z",
#             "60001618",
#             "1",
#             "5560458256",
#             "1.0",
#             "region",
#             "30002770",
#             "1228",
#             "124437",
#             "124758",
#         ),
#         (
#             "90",
#             "True",
#             "2019-10-23T17:33:02Z",
#             "60004099",
#             "1",
#             "5528738856",
#             "1.0",
#             "region",
#             "30002779",
#             "33475",
#             "10",
#             "10",
#         ),
#         (
#             "365",
#             "True",
#             "2019-12-12T22:29:48Z",
#             "60000322",
#             "1",
#             "911203378",
#             "120.73",
#             "station",
#             "30002744",
#             "3673",
#             "70376",
#             "70376",
#         ),
#         (
#             "365",
#             "True",
#             "2019-12-12T22:29:48Z",
#             "60000325",
#             "1",
#             "911203379",
#             "120.73",
#             "station",
#             "30002746",
#             "3673",
#             "70376",
#             "70376",
#         ),
#         (
#             "365",
#             "True",
#             "2019-12-12T22:29:48Z",
#             "60000328",
#             "1",
#             "911203380",
#             "120.73",
#             "station",
#             "30002748",
#             "3673",
#             "70376",
#             "70376",
#         ),
#         (
#             "365",
#             "True",
#             "2019-12-12T22:29:48Z",
#             "60000331",
#             "1",
#             "911203381",
#             "120.73",
#             "station",
#             "30002748",
#             "3673",
#             "70376",
#             "70376",
#         ),
#     ]
#     return data
