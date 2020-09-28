"""Utilities for dealing with files.

Version: 1.3.0
Last_Edit: 2020-09-09T17:54:06Z
"""
__version__ = "1.3.0"

import json
import logging
from pathlib import Path
from typing import Any, Iterable

#### setting up logger ####
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def load_json(file_path: Path, **kwargs) -> Any:
    """
    Load a json file.

    :param file_path: :py:class:`pathlib.Path` to the json file.
    :param `**kwargs`: Addtional key word arguments supplied to :func:`json.load()`.
    :raises Exception: Any exception raised during the loading of the file, or the conversion to json.
    :return: The loaded json file.
    """

    try:
        with open(file_path, "r") as json_file:
            data = json.load(json_file, **kwargs)
        return data
    except Exception as error:
        logger.exception(
            "Error trying to load json file from %s", file_path, exc_info=True
        )
        raise error


def save_json(
    data: Any,
    file_path: Path,
    mode: str = "w",
    indent: int = 2,
    sort_keys: bool = False,
    parents: bool = False,
    exist_ok: bool = True,
    **kwargs,
):
    """
    Save a json file. Can create parent directories if necessary.

    'w' for writing (truncating the file if it already exists), 'x' for exclusive
    creation.

    :param data: Data to save to json file.
    :param file_path: Output :py:class:`pathlib.Path` to json file.
    :param mode: File mode to use. As used in :func:`open`. Limited to 'w' or 'x'. Defaults to 'w'.
    :param indent: Spaces to indent json output. Defaults to 2.
    :param sort_keys: Sort key of json dicts. Defaults to ``False``.
    :param parents: Make parent directories if they don't exist. As used by :func:`pathlib.Path.mkdir()`. Defaults to ``False``.
    :param exist_ok: Suppress exception if parent directory exists as directory. As used by :func:`pathlib.Path.mkdir`. Defaults to ``True``.
    :param `**kwargs`: Addtional key word arguments supplied to :func:`json.dump()`.
    :raises ValueError: If unsupported file mode is used.
    :raises Exception: Any exception raised during the saving of the file, or the conversion from json.
    """

    kwargs["indent"] = indent
    kwargs["sort_keys"] = sort_keys

    try:
        if mode not in ["w", "x"]:
            raise ValueError(f"Unsupported file mode '{mode}'.")
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
        with open(file_path, mode) as json_file:
            json.dump(data, json_file, **kwargs)
    except Exception as error:
        logger.exception(
            "Error trying to save json data to %s", file_path, exc_info=True
        )
        raise error


def save_string(
    data: str,
    file_path: Path,
    mode: str = "w",
    parents: bool = False,
    exist_ok: bool = True,
    **kwargs,
) -> int:
    """
    Save a string. Makes parent directories if they don't exist.

    'w' for writing (truncating the file if it already exists), 'x' for exclusive
    creation and 'a' for appending

    :param data: The string to save.
    :param file_path: :py:class:`pathlib.Path` to saved file.
    :param mode: File mode to use. As used in :func:`open()`. Limited to 'w','x', or 'a'. Defaults to 'w'.
    :param parents: Make parent directories if they don't exist. As used by :func:`pathlib.Path.mkdir()`. Defaults to ``False``.
    :param exist_ok: Suppress exception if parent directory exists as directory. As used by :func:`pathlib.Path.mkdir()`. Defaults to ``True``.
    :param `**kwargs`: Additional key word arguments supplied to :func:`open()`.
    :raises ValueError: If unsupported file mode is used.
    :raises Exception: Any exception raised during the saving of the file.
    :return: return number of characters written.
    """
    try:

        if mode not in ["w", "x", "a"]:
            raise ValueError(f"Unsupported file mode '{mode}'.")
        if parents:
            file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
        with file_path.open(mode, **kwargs) as file_out:
            count = file_out.write(data)
        return count
    except Exception as error:
        logger.exception(
            "Error trying to save string data to %s", file_path, exc_info=True
        )
        raise error


def save_lines(
    data: Iterable[str],
    file_path: Path,
    mode: str = "w",
    line_separator: str = "\n",
    parents: bool = False,
    exist_ok: bool = True,
    **kwargs,
):
    r"""
    Write a sequence of strings as lines to a file.

    'w' for writing (truncating the file if it already exists), 'x' for exclusive
    creation and 'a' for appending

    :param data: The sequence of lines to save.
    :param file_path: :py:class:`pathlib.Path` to saved file.
    :param mode: File mode to use. As used in `open`. Limited to 'w','x', or 'a'. Defaults to 'w'.
    :param line_separator: Separate lines with this. Defaults to ``"\n"``.
    :param parents: Make parent directories if they don't exist. As used by :func:`pathlib.Path.mkdir()`.
        Defaults to ``False``.
    :param exist_ok: Suppress exception if parent directory exists as directory. As used by :py:func:`pathlib.Path.mkdir`. Defaults to ``True``.
    :param `**kwargs`: Addtional key word arguments supplied to :func:`open()`.
    :raises ValueError: If unsupported file mode is used.
    :raises Exception: Any exception raised during the saving of the file.
    """

    try:
        if mode not in ["w", "x", "a"]:
            raise ValueError(f"Unsupported file mode '{mode}'.")
        if parents:
            file_path.parent.mkdir(parents=parents, exist_ok=exist_ok)
        with file_path.open(mode, **kwargs) as file_out:
            if line_separator:
                file_out.writelines((f"{x}{line_separator}" for x in data))
            else:
                file_out.writelines(data)
    except Exception as error:
        logger.exception("Error trying to save lines to %s", file_path, exc_info=True)
        raise error


def save_stringables(
    iterable_stringable: Iterable[Any],
    file_path: Path,
    mode: str = "w",
    line_separator: str = "\n",
    parents: bool = False,
    exist_ok: bool = True,
    **kwargs,
):
    r"""
    Save an iterable that can be converted to a string via :func:`str()`.

    :param iterable_stringable: An iterable containing objects that can be turned into
        strings with :func:`str()`.
    :param file_path: :py:class:`pathlib.Path` to saved file.
    :param mode: File mode to use. As used in `open`. Limited to 'w','x', or 'a'. Defaults to 'w'.
    :param line_separator: Separate lines with this. Defaults to ``"\n"``.
    :param parents: Make parent directories if they don't exist. As used by :func:`pathlib.Path.mkdir`.
        Defaults to ``False``.
    :param exist_ok: Suppress exception if parent directory exists as directory. As used by :func:`pathlib.Path.mkdir`. Defaults to ``True``.
    :param `**kwargs`: Additional key word arguments supplied to :func:`open()`.
    :raises ValueError: If unsupported file mode is used.
    :raises Exception: Any exception raised during the saving of the file.
    """
    str_itr = (str(x) for x in iterable_stringable)
    save_lines(
        str_itr,
        file_path=file_path,
        mode=mode,
        line_separator=line_separator,
        parents=parents,
        exist_ok=exist_ok,
        **kwargs,
    )
