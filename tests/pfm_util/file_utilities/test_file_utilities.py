import json
from pathlib import Path
from typing import Sequence

import pytest

from pfm_util.file_utilities import file_utilities


@pytest.fixture(scope="module")
def test_path_root(tmp_path_factory):
    file_test_root = tmp_path_factory.mktemp("file_util")
    return file_test_root


@pytest.fixture(scope="module")
def json_data():
    data = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    return data


@pytest.fixture(scope="module")
def json_test_file_path(test_path_root: Path, json_data):
    file_name = "test_data.json"
    file_path: Path = test_path_root / file_name
    with open(file_path, "w") as json_file:
        json.dump(json_data, json_file)
    return file_path


@pytest.fixture(scope="module")
def delta_root(test_path_root):
    root_path: Path = test_path_root / Path("test_files")
    root_path.mkdir()

    return root_path


@pytest.fixture(scope="module")
def delta_files(delta_root: Path):
    branch_1 = delta_root / Path("branch_1/alpha/bravo/charlie/delta/echo")
    branch_1.mkdir(parents=True)
    branch_2 = delta_root / Path("branch_2/one/two/three")
    branch_2.mkdir(parents=True)
    files = []
    file_1 = delta_root / Path("branch_2/one") / Path("uno.txt")
    file_1.touch()
    files.append(file_1)
    file_2 = delta_root / Path("branch_2/one/two") / Path("dos.txt")
    file_2.touch()
    files.append(file_2)
    file_3 = delta_root / Path("branch_2/one/two/three") / Path("tres.txt")
    file_3.touch()
    files.append(file_3)
    return files


def test_load_json(json_data, json_test_file_path):
    loaded_data = file_utilities.load_json(json_test_file_path)
    assert loaded_data == json_data


def test_save_json(json_data, tmp_path):
    file_name = "test_data.json"
    file_path_sub_1 = "foo_json/bar"
    file_path_sub_2 = "bar_json/foo"
    file_path_1 = tmp_path / file_path_sub_1 / file_name
    file_path_2 = tmp_path / file_path_sub_2 / file_name
    # test for creation of file, with parents
    file_utilities.save_json(json_data, file_path_1, mode="w", parents=True)
    # expect failure due to not creating parent dirs
    with pytest.raises(FileNotFoundError):
        file_utilities.save_json(json_data, file_path_2, mode="w", parents=False)
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        file_utilities.save_json(json_data, file_path_1, mode="x", parents=True)
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        file_utilities.save_json(json_data, file_path_1, mode="p", parents=True)


def test_save_string(json_data, tmp_path):
    string_data = json.dumps(json_data)
    string_length = len(string_data)
    # test for creation of file, with parents
    file_path = tmp_path / "foo/saved_string.txt"
    saved_length = file_utilities.save_string(
        string_data, file_path, mode="w", parents=True
    )
    assert string_length == saved_length
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        saved_length = file_utilities.save_string(string_data, file_path, mode="x")
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        file_utilities.save_string(string_data, file_path, mode="p")
    # expect failure due to not creating parent dirs
    file_path = tmp_path / "bar/saved_string.txt"
    with pytest.raises(FileNotFoundError):
        file_utilities.save_string(string_data, file_path, mode="x", parents=False)


def test_save_lines(tmp_path):
    data = ["line1", "line2", "line3"]
    # test for creation of file, with parents
    file_path = tmp_path / "foo/saved_lines.txt"
    file_utilities.save_lines(data, file_path, mode="w", parents=True)
    saved_length = len(open(file_path).readlines())
    print(file_path)
    assert len(data) == saved_length
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        file_utilities.save_lines(data, file_path, mode="x", parents=True)
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        file_utilities.save_lines(data, file_path, mode="p", parents=True)
    # expect failure due to not creating parent dirs
    file_path = tmp_path / "bar/saved_lines.txt"
    with pytest.raises(FileNotFoundError):
        file_utilities.save_lines(data, file_path, mode="x")


def test_save_stringable(tmp_path):
    data = [Path("foo/line1"), Path("line2"), "line3", 4]
    # test for creation of file, with parents
    file_path = tmp_path / "foo/saved_stringables.txt"
    file_utilities.save_stringables(data, file_path, mode="w", parents=True)
    saved_length = len(open(file_path).readlines())
    print(file_path)
    assert len(data) == saved_length
    # expect failure due to file already existing and mode 'x'
    with pytest.raises(FileExistsError):
        file_utilities.save_stringables(data, file_path, mode="x", parents=True)
    # expect failure due to incorrect mode.
    with pytest.raises(ValueError):
        file_utilities.save_stringables(data, file_path, mode="p", parents=True)
    # expect failure due to not creating parent dirs
    file_path = tmp_path / "bar/saved_stringables.txt"
    with pytest.raises(FileNotFoundError):
        file_utilities.save_stringables(data, file_path, mode="x")


def test_delta_path():
    base_path = Path("/home/croaker/projects")
    item_path = Path("/home/croaker/projects/foo/bar.txt")
    new_base_path = Path("/home/croaker/tmp")
    # standard path delta
    delta_path = file_utilities.delta_path(base_path, item_path, new_base_path)
    assert delta_path == Path("/home/croaker/tmp/foo/bar.txt")
    # expect failure due to no common base path
    item_path = Path("/home2/croaker/projects/foo/bar.txt")
    with pytest.raises(ValueError):
        file_utilities.delta_path(base_path, item_path, new_base_path)
    # works correctly when only a file is left in stub
    item_path = Path("/home/croaker/projects/bar.txt")
    delta_path = file_utilities.delta_path(base_path, item_path, new_base_path)
    assert delta_path == Path("/home/croaker/tmp/bar.txt")


def test_collect_paths(delta_root: Path, delta_files: Sequence[Path]):
    def uno_filter(path: Path) -> bool:
        return "uno" in path.name

    found = file_utilities.collect_paths(delta_root, "**/*", uno_filter)
    found = list(found)
    assert len(found) == 1
    assert found[0].name == "uno.txt"
    found = file_utilities.collect_paths(delta_root, "**/*")
    found = list(found)
    assert len(found) == 13
    # expect failure if base path is not a directory or does not exist
    with pytest.raises(ValueError):
        non_exist = delta_root / Path("janet")
        found = file_utilities.collect_paths(non_exist, "**/*")
        # Generator must be accessed to trigger exception
        found = list(found)
    with pytest.raises(ValueError):
        found = file_utilities.collect_paths(delta_files[0], "**/*")
        # Generator must be accessed to trigger exception
        found = list(found)


def test_delta_paths(delta_root: Path, delta_files: Sequence[Path]):
    base_path = delta_root / Path("branch_2")
    new_base_path = delta_root / Path("branch_1")
    new_paths = file_utilities.delta_paths(base_path, "**/*", new_base_path)
    new_paths = list(new_paths)
    for path in new_paths:
        path_string = str(path)
        stub = path_string.replace(str(base_path), "")
        assert new_base_path / Path(stub) == path
    # expect failure if base path is not a directory or does not exist
    with pytest.raises(ValueError):
        non_exist = delta_root / Path("janet")
        found = file_utilities.delta_paths(non_exist, "**/*", new_base_path)
        # Generator must be accessed to trigger exception
        found = list(found)

    def uno_filter(path: Path) -> bool:
        return "uno" in path.name

    new_paths = file_utilities.delta_paths(base_path, "**/*", new_base_path, uno_filter)
    new_paths = list(new_paths)
    assert len(new_paths) == 1
    for path in new_paths:
        path_string = str(path)
        stub = path_string.replace(str(base_path), "")
        assert new_base_path / Path(stub) == path
