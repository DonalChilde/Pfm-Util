import logging
from pathlib import Path
from typing import Callable, Generator, Optional

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def delta_path(base_path: Path, item_path: Path, new_base_path: Path) -> Path:
    """
    Removes a base path from an item, and appends result to a new path

    :param base_path: The :py:class:`pathlib.Path` to be removed from `item_path`
    :param item_path: The :py:class:`pathlib.Path` to be delta-ed
    :param new_base_path: The new base :py:class:`pathlib.Path` for `item_path`.
    :raises ValueError: If base_path is not a sub-path of item_path.
    :return: The new combined path.
    """

    path_stub = item_path.relative_to(base_path)
    new_item_path = new_base_path / path_stub
    return new_item_path


# @dataclass
# class PathInOut:
#     path_in: Path
#     path_out: Path


def delta_paths(
    base_path: Path,
    glob_pattern: str,
    new_base_path: Path,
    path_filter: Optional[Callable[[Path], bool]] = None,
) -> Generator[Path, None, None]:
    """
    Generate a list of paths having a base path removed and replaced by a new base path.

    Paths have `base_path` removed, and the resulting path fragment is
    appended to `new_base_path`.

    :Example:
        Make an example here.

    :param base_path: The starting :py:class:`pathlib.Path`.
    :param glob_pattern: Glob pattern to match, using `base_path`. e.g `"*"` or `"**/*"`
    :param new_base_path: The new base path.
    :param path_filter: An additional filter to use for things that are hard to descirbe with glob.
        Defaults to ``None``.
    :raises ValueError: `base_path` must exist and be a directory.
    :yield: The new combined paths.
    """

    if not base_path.is_dir():
        raise ValueError(f"{base_path} - Not a directory or does not exist.")
    paths_in = collect_paths(
        base_path=base_path, glob_pattern=glob_pattern, path_filter=path_filter
    )
    for path_in in paths_in:
        path_out = delta_path(base_path, path_in, new_base_path)
        yield path_out


def collect_paths(
    base_path: Path,
    glob_pattern: str,
    path_filter: Optional[Callable[[Path], bool]] = None,
) -> Generator[Path, None, None]:
    """
    Collect paths using base_path.glob(), and apply a filter

    :param base_path: A starting :py:class:`pathlib.Path`
    :param glob_pattern: Glob pattern to match. e.g `"*"` or `"**/*"`
    :param path_filter: A custom filter for more complex matching than can be provided by glob. Defaults to ``None``.
    :raises ValueError: input_base_path must exist and be a directory.
    :yield: The matched paths.
    """

    # default content filter.
    def pass_through(_path_in: Path):
        return True

    if path_filter is None:
        path_filter = pass_through
    if not base_path.is_dir():
        raise ValueError(f"{base_path} - Not a directory or does not exist.")
    paths_in = base_path.glob(glob_pattern)
    for path_in in paths_in:
        if path_filter(path_in):
            yield path_in
