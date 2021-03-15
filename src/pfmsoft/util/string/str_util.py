"""Utilities for dealing with strings.

Version: 1.0
Last_Edit: 2019-10-21T14:45:20Z
"""
from typing import Any


def stringInsert():
    # TODO refine
    # https://stackoverflow.com/questions/30232344/insert-a-string-before-a-substring-of-a-string

    line = "Kong Panda"
    index = line.find("Panda")
    output_line = line[:index] + "Fu " + line[index:]
    assert output_line == "Kong Fu Panda"


def safeStrip(value: Any) -> Any:
    """Strip whitespace from a string value, if value is a string.

    :param value: possible string to strip
    :returns: Stripped string if value was string, else original value.
    """
    if isinstance(value, str):
        new_value = value.strip()
        return new_value
    else:
        return value


def strip_end(text: str, suffix: str, case_insensitive: bool = False) -> str:
    """Strips the suffix from a string if present.

    https://stackoverflow.com/a/1038999

    :param text: String to check for suffix
    :param suffix: Suffix to look for.
    :param case_insensitive: Do a case insensitive match. Defaults to False.
    :returns: The resulting string.
    """
    if case_insensitive:
        if not text.lower().endswith(suffix.lower()):
            return text
    else:
        if not text.endswith(suffix):
            return text
    return text[: len(text) - len(suffix)]


# TODO make strip_beginning
# TODO renamee to avoid strip() confusion?
