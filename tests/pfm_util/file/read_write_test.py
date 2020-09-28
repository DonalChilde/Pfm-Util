import json
from pathlib import Path

import pytest

from pfm_util.file.read_write import (
    load_json,
    save_json,
    save_lines,
    save_string,
    save_stringables,
)


def test_load_json(json_data, json_test_file_path):
    loaded_data = load_json(json_test_file_path)
    assert loaded_data == json_data


def test_save_json(json_data, tmp_path):
    file_name = "test_data.json"
    file_path_sub_1 = "foo_json/bar"
    file_path_sub_2 = "bar_json/foo"
    file_path_1 = tmp_path / file_path_sub_1 / file_name
    file_path_2 = tmp_path / file_path_sub_2 / file_name
    # test for creation of file, with parents
    save_json(json_data, file_path_1, mode="w", parents=True)
    # expect failure due to not creating parent dirs
    with pytest.raises(FileNotFoundError):
        save_json(json_data, file_path_2, mode="w", parents=False)
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        save_json(json_data, file_path_1, mode="x", parents=True)
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        save_json(json_data, file_path_1, mode="p", parents=True)


def test_save_string(json_data, tmp_path):
    string_data = json.dumps(json_data)
    string_length = len(string_data)
    # test for creation of file, with parents
    file_path = tmp_path / "foo/saved_string.txt"
    saved_length = save_string(string_data, file_path, mode="w", parents=True)
    assert string_length == saved_length
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        saved_length = save_string(string_data, file_path, mode="x")
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        save_string(string_data, file_path, mode="p")
    # expect failure due to not creating parent dirs
    file_path = tmp_path / "bar/saved_string.txt"
    with pytest.raises(FileNotFoundError):
        save_string(string_data, file_path, mode="x", parents=False)


def test_save_lines(tmp_path):
    data = ["line1", "line2", "line3"]
    # test for creation of file, with parents
    file_path = tmp_path / "foo/saved_lines.txt"
    save_lines(data, file_path, mode="w", parents=True)
    saved_length = len(open(file_path).readlines())
    print(file_path)
    assert len(data) == saved_length
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        save_lines(data, file_path, mode="x", parents=True)
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        save_lines(data, file_path, mode="p", parents=True)
    # expect failure due to not creating parent dirs
    file_path = tmp_path / "bar/saved_lines.txt"
    with pytest.raises(FileNotFoundError):
        save_lines(data, file_path, mode="x")


def test_save_stringable(tmp_path):
    data = [Path("foo/line1"), Path("line2"), "line3", 4]
    # test for creation of file, with parents
    file_path = tmp_path / "foo/saved_stringables.txt"
    save_stringables(data, file_path, mode="w", parents=True)
    saved_length = len(open(file_path).readlines())
    print(file_path)
    assert len(data) == saved_length
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        save_stringables(data, file_path, mode="x", parents=True)
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        save_stringables(data, file_path, mode="p", parents=True)
    # expect failure due to not creating parent dirs
    file_path = tmp_path / "bar/saved_stringables.txt"
    with pytest.raises(FileNotFoundError):
        save_stringables(data, file_path, mode="x")
