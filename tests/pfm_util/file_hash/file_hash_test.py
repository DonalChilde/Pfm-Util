"""

"""
# TODO test raising exceptions
import hashlib
import string
from pathlib import Path

import pytest

from pfm_util.file_hash import file_hash


@pytest.fixture(scope="function")
def hash_test_data(tmp_path):

    test_data_root_dir = tmp_path / "file_hash_test_data"
    test_data_root_dir.mkdir(exist_ok=True)

    print(test_data_root_dir)
    test_path_1 = test_data_root_dir / "test_file_1.txt"
    test_path_2 = test_data_root_dir / "test_file_2.txt"
    test_path_3 = test_data_root_dir / "test_file_3.txt"
    test_path_4 = test_data_root_dir / ".test_file_4.txt"
    test_data = {
        "test_data_root_dir": test_data_root_dir,
        "test_files": {
            "test_data_1": {"data": b"", "test_path": test_path_1},
            "test_data_2": {
                "data": b"this is a single line of text",
                "test_path": test_path_2,
            },
            "test_data_3": {
                "data": b"this is several lines of text.\nThe second line.\nThe third line.",
                "test_path": test_path_3,
            },
            "test_data_4": {
                "data": b"""A tripple quote
                        multiline
                        string.
                        """,
                "test_path": test_path_4,
            },
        },
    }

    for _, value in test_data["test_files"].items():
        with open(value["test_path"], "w+b") as out_file:
            out_file.write(value["data"])
    return test_data


def test_open_type():
    file_path = Path(__file__)
    with open(file_path, "rb") as binary_read:
        print(type(binary_read))
    with open(file_path, "r") as binary_read:
        print(type(binary_read))
    # assert False


def test_hashlib_type():
    hash_lib = hashlib.md5()
    print(type(hash_lib))
    hash_lib = hashlib.blake2b()
    print(type(hash_lib))
    # assert False


def test_guarantee_hashers():
    hashers = hashlib.algorithms_guaranteed
    print(hashers)
    # assert False


def is_hex(test_string: str):
    """test whether a string contains only hexadecimal digits

    https://stackoverflow.com/a/11592292/105844

    Arguments:
        s {str} -- [description]

    Returns:
        [type] -- [description]
    """
    hex_digits = set(string.hexdigits)
    # if test_string is long, then it is faster to check against a set
    return all(c in hex_digits for c in test_string)


def test_file_hash(hash_test_data):
    # file_path = Path(__file__)
    file_path = hash_test_data["test_files"]["test_data_1"]["test_path"]
    result = file_hash.file_hasher(file_path, "md5")
    md5_hash = md5sum(file_path)
    assert is_hex(result.file_hash)
    assert result.file_hash == md5_hash
    assert result.file_path == file_path
    assert result.hash_method == "md5"
    # with capsys.disabled():
    #     print([result.file_hash, md5_hash, file_path])


def md5sum(filename, blocksize=65536):
    # https://stackoverflow.com/a/21565932/105844
    hash_ = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash_.update(block)
    return hash_.hexdigest()


def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    # https://stackoverflow.com/a/3431835/105844
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()


def file_as_blockiter(afile, blocksize=65536):
    # https://stackoverflow.com/a/3431835/105844
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)


def test_md5_methods():
    # file_path = Path(__file__).parent / "__init__.py"
    file_path = Path(__file__)
    hash_1 = md5sum(file_path)
    hash_2 = None
    with open(file_path, "rb") as file_in:
        hash_2 = hash_bytestr_iter(
            file_as_blockiter(file_in), hashlib.md5(), ashexstr=True
        )
    assert hash_1 == hash_2
    hash_3 = file_hash.calculate_file_hash_from_path(file_path, hashlib.md5())
    assert hash_1 == hash_3
    print(hash_1)


def test_file_hash_generator(hash_test_data):
    dir_path: Path = hash_test_data["test_data_root_dir"]
    file_path_list = list(dir_path.glob("**/*"))
    f_gen = file_hash.file_hasher_generator(file_path_list, "md5")
    from_list = [
        file_hash.file_hasher(file_path, "md5")
        for file_path in file_path_list
        if file_path.is_file()
    ]
    from_generator = list(f_gen)
    print(f"from_list: {from_list}")
    print(f"from Generator: {from_generator}")

    assert from_list == from_generator
    assert len(from_list) == 4
    for value in from_list:
        assert isinstance(value, file_hash.FileHash)
        assert is_hex(value.file_hash)
        assert md5sum(value.file_path) == value.file_hash
    for value in from_generator:
        assert isinstance(value, file_hash.FileHash)
        assert is_hex(value.file_hash)
        assert md5sum(value.file_path) == value.file_hash


def test_file_hash_generator2(hash_test_data):
    dir_path = Path(__file__).parent
    file_path_list = dir_path.glob("**/*")
    f_gen = file_hash.file_hasher_generator(file_path_list, "md5")
    total_count = 0
    for count, value in enumerate(f_gen):
        total_count = count + 1
        assert isinstance(value, file_hash.FileHash)
        assert is_hex(value.file_hash)
        assert md5sum(value.file_path) == value.file_hash
    assert total_count > 1
    print(f"Files: {total_count}")


def test_all_hashers(hash_test_data):
    test_data = hash_test_data
    for hash_method in file_hash.HASH_METHODS:
        print(f"hash_method: {hash_method}")
        for _, value in test_data["test_files"].items():
            hasher = file_hash.get_hasher(hash_method)
            hasher.update(value["data"])
            string_hash = hasher.hexdigest()
            file_hash_data = file_hash.file_hasher(value["test_path"], hash_method)
            assert string_hash == file_hash_data.file_hash
