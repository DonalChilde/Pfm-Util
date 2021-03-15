"""Utilities for dealing with UUID.

Version: 1.0
Last_Edit: 2019-09-07T18:10:57Z
"""

import time
import uuid
from random import choices
from string import ascii_letters
from typing import Optional, Union

RANDOM_SALT = "".join(choices(ascii_letters, k=5))


def generate_uuid3(uuid_dns: uuid.UUID, salt_str: Optional[str] = None) -> uuid.UUID:
    """
    Generates a uuid3 uuid with a randomly generated salt.

    The salt is a combination of str(time()) and a random 5 character string.

    Optionally, the salt can be provided.

    :note: I am not sure what the point of this now, and I can no longer remember what
        problem I was trying to solve.

    :param uuid_dns: A uuid to be used for the namespace.
    :param salt_str: Optional provided salt. (default: {None})
    :returns: A uuid3 uuid.
    """
    if salt_str is not None:
        generated_uuid = uuid.uuid3(uuid_dns, str(salt_str))
    else:
        generated_uuid = uuid.uuid3(uuid_dns, str(time.time()) + RANDOM_SALT)
    return generated_uuid


def deserialize_uuid(uuid_string: Union[str, None]) -> Union[uuid.UUID, None]:
    """
    Deserialize a uuid. Used with db's? sqlite?

    :param uuid_string: [description]
    :return: [description]
    """
    if not uuid_string:
        return None
    else:
        return uuid.UUID(uuid_string)
