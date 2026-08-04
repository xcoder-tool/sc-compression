import enum
import re
from enum import IntEnum, auto

MAGIC_SC: bytes = b"SC"
MAGIC_SCLZ: bytes = b"SCLZ"
MAGIC_SIG: bytes = b"Sig:"
MAGIC_ZSTD: bytes = b"\x28\xb5\x2f\xfd"


_lzma_detection_pattern = re.compile(b"\x00\x00?\x00")


@enum.unique
class Signatures(IntEnum):
    NONE = auto()
    LZMA = auto()
    SC = auto()
    SCLZ = auto()
    SIG = auto()
    ZSTD = auto()


def get_signature(buffer: bytes) -> Signatures:
    signature = Signatures.NONE

    if _lzma_detection_pattern.match(buffer[1:5]):
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
