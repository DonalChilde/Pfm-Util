from pathlib import Path
from typing import Sequence

import pytest

from pfm_util.file.path import collect_paths, delta_path, delta_paths


def test_delta_path():
    base_path = Path("/home/croaker/projects")
    item_path = Path("/home/croaker/projects/foo/bar.txt")
    new_base_path = Path("/home/croaker/tmp")
    # standard path delta
    result = delta_path(base_path, item_path, new_base_path)
    assert result == Path("/home/croaker/tmp/foo/bar.txt")
    # expect failure due to no common base path
    item_path = Path("/home2/croaker/projects/foo/bar.txt")
    with pytest.raises(ValueError):
        delta_path(base_path, item_path, new_base_path)
    # works correctly when only a file is left in stub
    item_path = Path("/home/croaker/projects/bar.txt")
    result = delta_path(base_path, item_path, new_base_path)
    assert result == Path("/home/croaker/tmp/bar.txt")


def test_collect_paths(delta_root: Path, delta_files: Sequence[Path]):
    def uno_filter(path: Path) -> bool:
        return "uno" in path.name

    found = collect_paths(delta_root, "**/*", uno_filter)
    found = list(found)
    assert len(found) == 1
    assert found[0].name == "uno.txt"
    found = collect_paths(delta_root, "**/*")
    found = list(found)
    assert len(found) == 13
    # expect failure if base path is not a directory or does not exist
    with pytest.raises(ValueError):
        non_exist = delta_root / Path("janet")
        found = collect_paths(non_exist, "**/*")
        # Generator must be accessed to trigger exception
        found = list(found)
    with pytest.raises(ValueError):
        found = collect_paths(delta_files[0], "**/*")
        # Generator must be accessed to trigger exception
        found = list(found)


def test_delta_paths(delta_root: Path, delta_files: Sequence[Path]):
    base_path = delta_root / Path("branch_2")
    new_base_path = delta_root / Path("branch_1")
    new_paths = delta_paths(base_path, "**/*", new_base_path)
    new_paths = list(new_paths)
    for path in new_paths:
        path_string = str(path)
        stub = path_string.replace(str(base_path), "")
        assert new_base_path / Path(stub) == path
    # expect failure if base path is not a directory or does not exist
    with pytest.raises(ValueError):
        non_exist = delta_root / Path("janet")
        found = delta_paths(non_exist, "**/*", new_base_path)
        # Generator must be accessed to trigger exception
        found = list(found)

    def uno_filter(path: Path) -> bool:
        return "uno" in path.name

    new_paths = delta_paths(base_path, "**/*", new_base_path, uno_filter)
    new_paths = list(new_paths)
    assert len(new_paths) == 1
    for path in new_paths:
        path_string = str(path)
        stub = path_string.replace(str(base_path), "")
        assert new_base_path / Path(stub) == path
