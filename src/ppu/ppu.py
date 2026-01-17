class PPU:
    def __init__(self):
        # Регистры
        self.ctrl = 0x00
        self.mask = 0x00
        self.status = 0x00
        self.oam_addr = 0x00

        # Внутренние регистры
        self.vram_addr = 0x0000
        self.temp_addr = 0x0000
        self.fine_x = 0
        self.write_latch = 0  # 0 или 1

        self.data_buffer = 0x00

        # Память PPU (заглушка)
        self.vram = bytearray(0x4000)
        self.oam = bytearray(256)

    # ===== CPU READ =====

    def cpu_read(self, addr: int) -> int:
        reg = (addr - 0x2000) % 8

        if reg == 2:  # PPUSTATUS
            value = self.status
            self.status &= 0x7F      # сброс VBlank
            self.write_latch = 0     # сброс latch
            return value

        elif reg == 4:  # OAMDATA
            return self.oam[self.oam_addr]

        elif reg == 7:  # PPUDATA
            value = self.vram[self.vram_addr]

            if self.vram_addr < 0x3F00:
                ret = self.data_buffer
                self.data_buffer = value
            else:
                ret = value
                self.data_buffer = self.vram[self.vram_addr - 0x1000]

            self._increment_vram()
            return ret

        return 0

    # ===== CPU WRITE =====

    def cpu_write(self, addr: int, value: int):
        reg = (addr - 0x2000) % 8
        value &= 0xFF

        if reg == 0:  # PPUCTRL
            self.ctrl = value
            self.temp_addr = (self.temp_addr & 0xF3FF) | ((value & 0x03) << 10)

        elif reg == 1:  # PPUMASK
            self.mask = value

        elif reg == 3:  # OAMADDR
            self.oam_addr = value

        elif reg == 4:  # OAMDATA
            self.oam[self.oam_addr] = value
            self.oam_addr = (self.oam_addr + 1) & 0xFF

        elif reg == 5:  # PPUSCROLL
            if self.write_latch == 0:
                self.fine_x = value & 0x07
                self.temp_addr = (self.temp_addr & 0xFFE0) | (value >> 3)
                self.write_latch = 1
            else:
                self.temp_addr = (self.temp_addr & 0x8FFF) | ((value & 0x07) << 12)
                self.temp_addr = (self.temp_addr & 0xFC1F) | ((value & 0xF8) << 2)
                self.write_latch = 0

        elif reg == 6:  # PPUADDR
            if self.write_latch == 0:
                self.temp_addr = (self.temp_addr & 0x00FF) | ((value & 0x3F) << 8)
                self.write_latch = 1
            else:
                self.temp_addr = (self.temp_addr & 0xFF00) | value
                self.vram_addr = self.temp_addr
                self.write_latch = 0

        elif reg == 7:  # PPUDATA
            self.vram[self.vram_addr] = value
            self._increment_vram()

    def _increment_vram(self):
        inc = 32 if (self.ctrl & 0x04) else 1
        self.vram_addr = (self.vram_addr + inc) & 0x3FFF
