from struct import pack

from .common import get_endian_sign, Endian


class ByteWriter:
    def __init__(self, endian: Endian):
        self._buffer = bytearray()
        self._endian_sign = get_endian_sign(endian)

    def set_endian(self, endian: Endian) -> None:
        self._endian_sign = get_endian_sign(endian)

    def write(self, value: bytes) -> None:
        self._buffer += value

    def write_double(self, value: float) -> None:
        self.write(pack(f"{self._endian_sign}d", value))

    def write_float(self, value: float) -> None:
        self.write(pack(f"{self._endian_sign}f", value))

    def write_u_int64(self, integer: int):
        self.write(pack(f"{self._endian_sign}Q", integer))

    def write_int64(self, integer: int) -> None:
        self.write(pack(f"{self._endian_sign}q", integer))

    def write_u_int32(self, integer: int) -> None:
        self.write(pack(f"{self._endian_sign}I", integer))

    def write_int32(self, integer: int) -> None:
        self.write(pack(f"{self._endian_sign}i", integer))

    def write_u_int16(self, integer: int) -> None:
        self.write(pack(f"{self._endian_sign}H", integer))

    def write_int16(self, integer: int) -> None:
        self.write(pack(f"{self._endian_sign}h", integer))

    def write_u_int8(self, integer: int) -> None:
        self.write(pack(f"{self._endian_sign}B", integer))

    def write_int8(self, integer: int) -> None:
        self.write(pack(f"{self._endian_sign}b", integer))

    @property
    def buffer(self) -> bytes:
        return self._buffer

    @property
    def position(self):
        return len(self._buffer)
