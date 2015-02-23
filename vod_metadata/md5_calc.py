from io import open
import hashlib

__all__ = ["md5_checksum"]

def md5_checksum(file_path, chunk_bytes=4194304):
    """Return the MD5 checksum (hex digest) of the file"""

    with open(file_path, "rb") as infile:
        checksum = hashlib.md5()
        while 1:
            data = infile.read(chunk_bytes)
            if not data:
                break
            checksum.update(data)

    return checksum.hexdigest()
