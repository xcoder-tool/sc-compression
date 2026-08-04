import lzma
from contextlib import suppress
from typing import assert_never

from bytestream import BinaryReader

from .exceptions import CompressionUnsupported, UnknownFileMagicException
from .signatures import (
    MAGIC_SC,
    MAGIC_SCLZ,
    MAGIC_SIG,
    MAGIC_ZSTD,
    Signatures,
    get_signature,
)


class Decompressor:
    @classmethod
    def decompress(cls, buffer: bytes) -> bytes:
        signature = get_signature(buffer)
        match signature:
            case Signatures.NONE:
                return buffer

            case Signatures.SC:
                reader = BinaryReader(buffer, "big")

                cls.check_magic(MAGIC_SC, reader=reader)

                file_version = reader.read_uint()
                if file_version == 4:
                    file_version = reader.read_uint()

                if file_version == 0x05000000 or file_version == 0x06000000:
                    reader.endian = "little"

                    if file_version == 0x06000000:
                        _ = reader.read_ushort()

                    metadata_table_offset = (
                        reader.read_uint()
                    )  # offset to metadata vtable
                    reader.read(metadata_table_offset)  # metadata
                else:
                    hash_length = reader.read_uint()
                    _hash = reader.read(hash_length)
                    # TODO: validate hash?

                return cls.decompress(reader.read(-1))
            case Signatures.SIG:
                cls.check_magic(MAGIC_SIG, buffer=buffer[:4])
                # NOTE: Skips `SIG:` magic and 64-byte hash
                return cls.decompress(buffer[68:])
            case Signatures.SCLZ:
                with suppress(ImportError):
                    import lzham

                    reader = BinaryReader(buffer, "little")

                    cls.check_magic(MAGIC_SCLZ, reader=reader)

                    dict_size_log2 = reader.read_uchar()
                    uncompressed_size = reader.read_uint()

                    filters = {"dict_size_log2": dict_size_log2}

                    return lzham.decompress(reader.read(-1), uncompressed_size, filters)

                raise CompressionUnsupported(
                    "The 'lzham' extra is required for this module. "
                    "Please install this library using: sc-compression[lzham]"
                )
            case Signatures.LZMA:
                decompressor = lzma.LZMADecompressor()
                compressed = buffer[:5] + b"\xff" * 8 + buffer[9:]
                return decompressor.decompress(compressed)
            case Signatures.ZSTD:
                cls.check_magic(MAGIC_ZSTD, buffer=buffer)

                with suppress(ImportError):
                    from compression import zstd

                    return zstd.decompress(buffer)

                with suppress(ImportError):
                    from backports import zstd

                    return zstd.decompress(buffer)

                with suppress(ImportError):
                    import zstandard

                    decompressor = zstandard.ZstdDecompressor()
                    return decompressor.decompress(buffer)

                raise CompressionUnsupported(
                    "The 'zstd' extra is required for this module. "
                    "Please install this library using: sc-compression[zstd]"
                )
            case _:
                assert_never(signature)

    @staticmethod
    def check_magic(
        expected_magic: bytes,
        *,
        reader: BinaryReader | None = None,
        buffer: bytes | None = None,
    ) -> None:
        if reader is not None:
            magic = reader.read(len(expected_magic))
        elif buffer is not None:
            magic = buffer[: len(expected_magic)]
        else:
            raise ValueError("Cannot find buffer to get magic from.")

        if magic != expected_magic:
            raise UnknownFileMagicException(magic, magic, expected_magic)
