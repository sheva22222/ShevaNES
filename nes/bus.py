class Bus:
    def __init__(self):
        self.ram = bytearray(2048)
        self.prg = bytearray(32768)

    def read(self, addr):
        if addr < 0x2000:
            return self.ram[addr % 0x0800]
        elif addr >= 0x8000:
            return self.prg[addr - 0x8000]
        return 0

    def write(self, addr, value):
        if addr < 0x2000:
            self.ram[addr % 0x0800] = value
          
