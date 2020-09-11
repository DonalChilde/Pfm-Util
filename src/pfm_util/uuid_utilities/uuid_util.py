"""Utilities for dealing with UUID.

Version: 1.0
Last_Edit: 2019-09-07T18:10:57Z
"""

import uuid
from random import choices
from string import ascii_letters
from timeit import timeit
from typing import Union, Optional
import time

RANDOM_SALT = "".join(choices(ascii_letters, k=5))


def generate_uuid3(uuid_dns: uuid.UUID, salt_str: Optional[str] = None) -> uuid.UUID:
    """Generates a uuid3 uuid with a randomly generated salt.
    The salt is a combination of str(time()) and a random 5 character string.

    Optionally, the salt can be provided.
    
    Arguments:
        uuid_dns {uuid.UUID} -- A uuid to be used for the namespace.
    
    Keyword Arguments:
        salt_str {Optional[str]} -- Optional provided salt. (default: {None})
    
    Returns:
        uuid.UUID -- A uuid3 uuid.
    """
    if salt_str is not None:
        generated_uuid = uuid.uuid3(uuid_dns, str(salt_str))
    else:
        generated_uuid = uuid.uuid3(uuid_dns, str(time.time()) + RANDOM_SALT)
    return generated_uuid


def deserialize_uuid(uuid_string: Union[str, None]) -> Union[uuid.UUID, None]:
    if not uuid_string:
        return None
    else:
        return uuid.UUID(uuid_string)
