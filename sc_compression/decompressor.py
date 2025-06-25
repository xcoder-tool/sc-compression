import lzma

from sc_compression.exceptions import UnknownFileMagicException
from sc_compression.signatures import (
    Signatures,
    get_signature,
    MAGIC_SC,
    MAGIC_ZSTD,
    MAGIC_SCLZ,
)
from sc_compression.utils import ByteReader

try:
    import lzham
except ImportError:
    from platform import system as get_system_name

    lzham = None
    if get_system_name() == "Windows":
        from sc_compression.support.lzham import LZHAM

        lzham = LZHAM

try:
    import zstandard
except ImportError:
    zstandard = None


class Decompressor:
    def __init__(self):
        self.signature = Signatures.NONE
        self.file_version = -1
        self.hash = None

    def decompress(self, buffer: bytes) -> bytes:
        self.signature = get_signature(buffer)
        if self.signature == Signatures.NONE:
            return buffer

        if self.signature == Signatures.SC:
            reader = ByteReader(buffer, "big")

            self.check_magic(MAGIC_SC, reader=reader)

            self.file_version = reader.read_int32()
            if self.file_version == 4:
                self.file_version = reader.read_int32()

            if self.file_version == 0x05000000 or self.file_version == 0x06000000:
                reader.set_endian("little")

                if self.file_version == 0x06000000:
                    reader.read_int16()

                metadata_table_offset = reader.read_int32()  # offset to metadata vtable
                reader.read(metadata_table_offset)  # metadata
            else:
                hash_length = reader.read_int32()
                self.hash = reader.read(hash_length)

            return self.decompress(reader.read_all_bytes())
        elif self.signature == Signatures.SIG:
            return self.decompress(buffer[68:])
        elif self.signature == Signatures.SCLZ and lzham is not None:
            reader = ByteReader(buffer, "little")

            self.check_magic(MAGIC_SCLZ, reader=reader)

            dict_size_log2 = reader.read_u_int8()
            uncompressed_size = reader.read_int32()

            filters = {"dict_size_log2": dict_size_log2}
            return lzham.decompress(reader.read_all_bytes(), uncompressed_size, filters)
        elif self.signature == Signatures.LZMA:
            decompressor = lzma.LZMADecompressor()
            compressed = buffer[:5] + b"\xff" * 8 + buffer[9:]
            return decompressor.decompress(compressed)
        elif self.signature == Signatures.ZSTD and zstandard is not None:
            self.check_magic(MAGIC_ZSTD, buffer=buffer)

            decompressor = zstandard.ZstdDecompressor()
            return decompressor.decompress(buffer)
        else:
            raise TypeError(self.signature)

    @staticmethod
    def check_magic(
        expected_magic: bytes,
        reader: ByteReader | None = None,
        buffer: bytes | None = None,
    ) -> None:
        if reader is not None:
            magic = reader.read(len(expected_magic))
        elif buffer is not None:
            magic = buffer[: len(expected_magic)]
        else:
            raise Exception("Cannot find buffer to get magic from.")

        if magic != expected_magic:
            raise UnknownFileMagicException(magic, magic, expected_magic)
