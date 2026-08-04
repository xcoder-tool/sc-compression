from contextlib import suppress

from .exceptions import CompressionUnsupported


__all__ = ["compress", "decompress"]


def compress(data: bytes) -> bytes:
    with suppress(ImportError):
        from compression import zstd

        return zstd.compress(data)

    with suppress(ImportError):
        from backports import zstd

        return zstd.compress(data)

    with suppress(ImportError):
        import zstandard

        compressor = zstandard.ZstdCompressor()
        compressed = compressor.compress(data)

    raise CompressionUnsupported(
        "The 'zstd' extra is required for this module. "
        "Please try to install this library using: sc-compression[zstd] or update your Python to 3.14+ to use built-in compression.zstd library"
    )


def decompress(data: bytes) -> bytes:
    with suppress(ImportError):
        from compression import zstd

        return zstd.decompress(data)

    with suppress(ImportError):
        from backports import zstd

        return zstd.decompress(data)

    with suppress(ImportError):
        import zstandard

        decompressor = zstandard.ZstdDecompressor()
        return decompressor.decompress(data)

    raise CompressionUnsupported(
        "The 'zstd' extra is required for this module. "
        "Please install this library using: sc-compression[zstd]"
    )
