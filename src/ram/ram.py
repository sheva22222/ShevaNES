class InternalRAM:
    def __init__(self):
        self.mem = bytearray(0x800)  # 2 KB

    def read(self, addr: int) -> int:
        addr &= 0x07FF  # зеркалирование
        return self.mem[addr]

    def write(self, addr: int, value: int):
        addr &= 0x07FF  # зеркалирование
        self.mem[addr] = value & 0xFF
