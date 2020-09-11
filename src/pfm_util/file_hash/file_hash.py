# Last edited on 2019-12-30T16:56:40Z
"""A collection of file hashing utilities.
"""
import hashlib
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    ByteString,
    Callable,
    Dict,
    Iterator,
    NamedTuple,
    Optional,
    Sequence,
    Union,
)

VERSION = "1.0.0"


def hash_a_byte_str_iterator(
    bytes_iterator: Iterator[ByteString], hasher: Any, as_hex_str: bool = False
) -> Union[ByteString, str]:
    """
    Get the hash digest of a binary string iterator.

    https://stackoverflow.com/a/3431835/105844
    
    Parameters
    ----------
    bytes_iterator : Iterator[ByteString]
        The byte iterator
    hasher : Any
        The hash function from `hashlib`
    as_hex_str : {'False','True'}, optional
        Return the digest as bytes, or a hexidecimal string, by default False
    
    Returns
    -------
    Union[ByteString, str]
        The digest of the input bytes, as bytes or a hexidcimal string, by default bytes.
    """

    for block in bytes_iterator:
        hasher.update(block)
    return hasher.hexdigest() if as_hex_str else hasher.digest()


def file_as_block_iterator(
    file_handle: BinaryIO, block_size: int = 65536
) -> Iterator[ByteString]:
    """
    Make an iterator for a file opened in binary mode.

    https://stackoverflow.com/a/3431835/105844
    
    Parameters
    ----------
    file_handle : BinaryIO
        The handle for  file opened in binary mode.
    block_size : int, optional
        The size of the block bytes to read from the file, by default 65536
    
    Yields
    -------
    Iterator[ByteString]
        An iterator of bytes.
    """

    with file_handle:
        block = file_handle.read(block_size)
        while len(block) > 0:
            yield block
            block = file_handle.read(block_size)


def calculate_file_hash_from_path(
    file_path: Path, hasher: Any, block_size: int = 65536, as_hex_str: bool = True
) -> Union[ByteString, str]:
    """
    Calculate a hash digest for a given file path.

    https://stackoverflow.com/a/21565932/105844
    
    Parameters
    ----------
    file_path : Path
        The `pathlib.Path` to a file.
    hasher : Any
        The hash function from `hashlib`
    block_size : int, optional
        The size of the block bytes to read from the file, by default 65536
    as_hex_str : {'True','False'}, optional
        Return the digest as bytes, or a hexidecimal string, by default True
    
    Returns
    -------
    Union[ByteString, str]
        The digest of the file, as bytes or a hexidcimal string, by default bytes.
    
    Raises
    ------
    ValueError
        If the file_path does not exist or is not a file.
    """

    if not file_path.exists() or not file_path.is_file():
        raise ValueError(f"{file_path} is not a file or does not exist")

    with open(file_path, "rb") as file_in:
        result = calculate_file_hash_from_file_handle(
            file_in, hasher, block_size, as_hex_str
        )
        return result


def calculate_file_hash_from_file_handle(
    file_handle: BinaryIO, hasher: Any, block_size: int = 65536, as_hex_str: bool = True
) -> Union[ByteString, str]:
    """
    Calculate a hash digest for a given file handle opened in binary mode..

    https://stackoverflow.com/a/21565932/105844
    
    Parameters
    ----------
    file_handle : BinaryIO
        The handle for  file opened in binary mode.
    hasher : Any
        The hash function from `hashlib`
    block_size : int, optional
        The size of the block bytes to read from the file, by default 65536
    as_hex_str : {'True','False'}, optional
        Return the digest as bytes, or a hexidecimal string, by default True
    
    Returns
    -------
    Union[ByteString, str]
        The digest of the file, as bytes or a hexidcimal string, by default bytes.
    """
    result = hash_a_byte_str_iterator(
        bytes_iterator=file_as_block_iterator(
            file_handle=file_handle, block_size=block_size
        ),
        hasher=hasher,
        as_hex_str=as_hex_str,
    )
    return result


# The guaranteed available hash methods (Python 3.7).
HASH_METHODS: Dict[str, Callable] = {
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    # "shake_128": hashlib.shake_128,
    # "shake_256": hashlib.shake_256,
    "sha3_224": hashlib.sha3_224,
    "sha3_256": hashlib.sha3_256,
    "sha3_384": hashlib.sha3_384,
    "sha3_512": hashlib.sha3_512,
}


def get_hasher(hasher_name: str) -> Any:
    """
    Convenience method to get a hasher.

    Parameters
    ----------
    hasher_name : {'blake2b','blake2s','md5','sha1','sha224','sha256','sha384','sha512','sha3_224','sha3_256','sha3_384','sha3_512'}, str
        The name of a hasher.

    Returns
    -------
    Any
        A hash function from `hashlib`

    Raises
    ------
    ValueError
        If the requested name not found in `HASH_METHODS`
    """
    lc_hasher_name = hasher_name.lower()
    hasher: Optional[Callable] = HASH_METHODS.get(lc_hasher_name, None)
    if hasher is None:
        raise ValueError(
            f"Hasher {hasher_name} not found. Must be one of {HASH_METHODS.keys()}"
        )
    return hasher()


class FileHash(NamedTuple):
    """
    Data structure to hold return from `file_hash` and `file_hash_generator`
    
    Parameters
    ----------
    file_path : Path
    file_hash : str
    hash_method : str
    """

    file_path: Path
    file_hash: str
    hash_method: str

    def __repr__(self):
        return f"<FileHash(file_path={self.file_path}, file_hash={self.file_hash}, hash_method={self.hash_method})>"


def file_hasher(file_path: Path, hash_method: str) -> FileHash:
    """
    Convenience method to hash a file path.
    
    Parameters
    ----------
    file_path : Path
        The `pathlib.Path` to a file.
    hash_method : {'blake2b','blake2s','md5','sha1','sha224','sha256','sha384','sha512','sha3_224','sha3_256','sha3_384','sha3_512'}, str
        The name of a hasher.
    
    Returns
    -------
    FileHash : `FileHash`
    """
    hasher = get_hasher(hash_method)
    file_hash_str: str = calculate_file_hash_from_path(file_path, hasher)  # type: ignore
    return FileHash(file_path, file_hash_str, hash_method)


def file_hasher_generator(
    file_paths: Sequence[Path], hash_method: str
) -> Iterator[FileHash]:
    """
    Makes an iterator from a list of file paths that returns a `FileHash`
    
    Parameters
    ----------
    file_paths : Sequence[Path]
        A sequence of  `pathlib.Path`s to files.
    hash_method : {'blake2b','blake2s','md5','sha1','sha224','sha256','sha384','sha512','sha3_224','sha3_256','sha3_384','sha3_512'}, str
        The name of a hasher.
    
    Returns
    -------
    Iterator[`FileHash`]
    """
    generator = (
        file_hasher(file_path, hash_method)
        for file_path in file_paths
        if file_path.is_file()
    )
    return generator


def file_hasher_generator2(
    file_paths: Sequence[Path], hash_method: str, path_filter: Callable[[Path], bool]
) -> Iterator[FileHash]:
    """
    Makes an iterator from a list of file paths that returns a `FileHash`
    
    Parameters
    ----------
    file_paths : Sequence[Path]
        A sequence of  `pathlib.Path`s to files.
    hash_method : {'blake2b','blake2s','md5','sha1','sha224','sha256','sha384','sha512','sha3_224','sha3_256','sha3_384','sha3_512'}, str
        The name of a hasher.
    
    Returns
    -------
    Iterator[`FileHash`]
    """
    generator = (
        file_hasher(file_path, hash_method)
        for file_path in file_paths
        if path_filter(file_path)
    )
    return generator


class IsFilePath:
    def __call__(self, file_path: Path) -> bool:
        if file_path.exists() and file_path.is_file():
            return True
        return False
