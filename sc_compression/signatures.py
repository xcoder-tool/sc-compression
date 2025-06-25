import enum
import re
from enum import IntEnum

MAGIC_SC: bytes = b"SC"
MAGIC_SCLZ: bytes = b"SCLZ"
MAGIC_SIG: bytes = b"Sig:"
MAGIC_ZSTD: bytes = b"\x28\xb5\x2f\xfd"


@enum.unique
class Signatures(IntEnum):
    NONE = 0
    LZMA = 1
    SC = 2
    SCLZ = 3
    SIG = 4
    ZSTD = 5


def get_signature(buffer: bytes) -> Signatures:
    signature = Signatures.NONE

    if re.match(b"\x00\x00?\x00", buffer[1:5]):
        signature = Signatures.LZMA
    elif buffer.startswith(MAGIC_ZSTD):
        signature = Signatures.ZSTD

    if buffer.startswith(MAGIC_SCLZ):
        signature = Signatures.SCLZ
    elif buffer.startswith(MAGIC_SC):
        signature = Signatures.SC
    elif buffer.startswith(MAGIC_SIG):
        signature = Signatures.SIG

    return signature
