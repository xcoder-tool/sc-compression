import lzma
from contextlib import suppress
from hashlib import md5
from typing import ClassVar, assert_never

from bytestream import BinaryWriter

from .exceptions import CompressionUnsupported
from .signatures import MAGIC_SC, MAGIC_SCLZ, MAGIC_SIG, Signatures
from .zstd import compress as zstd_compress


class Compressor:
    LZHAM_FILTERS: ClassVar[dict[str, int]] = {"dict_size_log2": 18}
    LZMA_FILTERS: ClassVar[list[dict[str, int]]] = [
        {
            "id": lzma.FILTER_LZMA1,
            "dict_size": 256 * 1024,
            "lc": 3,
            "lp": 0,
            "pb": 2,
            "mode": lzma.MODE_NORMAL,
        },
    ]

    @classmethod
    def compress(
        cls,
        data: bytes,
        signature: Signatures,
        file_version: int,
        metadata: bytes | None = None,
    ) -> bytes:
        compressed = cls._compress_internal(data, signature, file_version)

        return cls._write_header(compressed, data, file_version, signature, metadata)

    @classmethod
    def _compress_internal(
        cls, data: bytes, signature: Signatures, file_version: int
    ) -> bytes:
        writer = BinaryWriter("little")
        if signature is Signatures.NONE:
            return data
        elif signature in (Signatures.LZMA, Signatures.SIG) or (
            signature == Signatures.SC and file_version != 3
        ):
            compressed = lzma.compress(
                data, format=lzma.FORMAT_ALONE, filters=cls.LZMA_FILTERS
            )

            writer.write(compressed[:5])

            writer.write_uint(len(data))

            writer.write(compressed[13:])

            return writer.buffer
        elif signature == Signatures.SCLZ:
            with suppress(ImportError):
                import lzham

                compressed = lzham.compress(data, filters=cls.LZHAM_FILTERS)

                writer.write(MAGIC_SCLZ)
                writer.write_uchar(cls.LZHAM_FILTERS["dict_size_log2"])
                writer.write_uint(len(data))
                writer.write(compressed)

                return writer.buffer

            raise CompressionUnsupported(
                "The 'lzham' extra is required for this module. "
                "Please try to install this library using: sc-compression[lzham]"
            )
        elif signature in (Signatures.SC, Signatures.ZSTD):
            return zstd_compress(data)
        else:
            assert_never(signature)

    @staticmethod
    def _write_header(
        compressed: bytes,
        data: bytes,
        file_version: int,
        signature: Signatures,
        metadata: bytes | None,
    ) -> bytes:
        if signature in (Signatures.SC, Signatures.SCLZ):
            if file_version <= 4:
                writer = BinaryWriter("big")
                writer.write(MAGIC_SC)
                writer.write_uint(file_version)
                if file_version == 4:
                    writer.write_uint(1)

                data_hash = md5(data).digest()

                writer.write_int(len(data_hash))
                writer.write(data_hash)
            else:
                writer = BinaryWriter("little")
                writer.write(MAGIC_SC)
                writer.write_uint(file_version)

                if file_version == 6:
                    writer.write_ushort(0)  # unknown

                if metadata is None:
                    writer.write_uint(0)
                else:
                    writer.write_uint(len(metadata))
                    writer.write(metadata)

            return writer.buffer + compressed
        elif signature == Signatures.SIG:
            writer = BinaryWriter("big")
            writer.write(MAGIC_SIG)
            writer.write(b"\x00" * 64)  # sha64
            return writer.buffer + compressed

        return compressed
