import json
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def test_path_root(tmp_path_factory):
    file_test_root = tmp_path_factory.mktemp("file_util")
    return file_test_root


@pytest.fixture(scope="module")
def json_data():
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
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
