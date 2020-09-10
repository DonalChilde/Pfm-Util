from pathlib import Path

import pytest
import types

from pfm_util.file_utilities import file_utilities


@pytest.fixture(scope="function")
def delta_path_test_data(tmp_path):
    # TODO make some test data here for collect_paths and delta_paths
    test_data_root_dir = tmp_path / "delta_path_test_data"
    test_data_root_dir.mkdir(exist_ok=True)


def test_delta_path_subdir():
    input_path_base = Path("/home/croaker/projects")
    item_path = Path("/home/croaker/projects/foo/bar.txt")
    output_path_base = Path("/home/croaker/tmp")
    delta_path = file_utilities.delta_path(input_path_base, item_path, output_path_base)
    assert delta_path == Path("/home/croaker/tmp/foo/bar.txt")


def test_delta_path_no_common():
    input_path_base = Path("/home/croaker/projects")
    item_path = Path("/home2/croaker/projects/foo/bar.txt")
    output_path_base = Path("/home/croaker/tmp")
    with pytest.raises(ValueError):
        file_utilities.delta_path(input_path_base, item_path, output_path_base)


def test_delta_path_no_subdir():
    input_path_base = Path("/home/croaker/projects")
    item_path = Path("/home/croaker/projects/bar.txt")
    output_path_base = Path("/home/croaker/tmp")
    delta_path = file_utilities.delta_path(input_path_base, item_path, output_path_base)
    assert delta_path == Path("/home/croaker/tmp/bar.txt")


def test_delta_paths():
    input_base_path = Path("/home/chad/projects/AAL-PBS-Data/")
    glob_pattern = "**/*.txt"
    output_base_path = Path("/home/chad/tmp")

    def path_filter(path: Path) -> bool:
        if "MIA" in path.name:
            return True
        else:
            return False

    new_paths = file_utilities.delta_paths(
        input_base_path=input_base_path,
        glob_pattern=glob_pattern,
        output_base_path=output_base_path,
        path_filter=path_filter,
    )
    assert isinstance(new_paths, types.GeneratorType)
    list_of_paths = list(new_paths)
    assert len(list_of_paths) > 0
    assert isinstance(list_of_paths[0], Path)


def test_collect_paths():
    input_base_path = Path("/home/chad/projects/AAL-PBS-Data/")
    glob_pattern = "**/*.txt"

    def path_filter(path: Path) -> bool:
        if "MIA" in path.name:
            return True
        else:
            return False

    collected_paths = file_utilities.collect_paths(
        input_base_path=input_base_path,
        glob_pattern=glob_pattern,
        path_filter=path_filter,
    )
    assert isinstance(collected_paths, types.GeneratorType)
    list_of_paths = list(collected_paths)
    assert len(list_of_paths) > 0
    assert isinstance(list_of_paths[0], Path)
