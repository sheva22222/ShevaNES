# cpu.py — NES CPU (Ricoh 2A03 / 6502)

FLAG_C = 0x01  # Carry
FLAG_Z = 0x02  # Zero
FLAG_I = 0x04  # Interrupt Disable
FLAG_D = 0x08  # Decimal (unused in NES)
FLAG_B = 0x10  # Break
FLAG_U = 0x20  # Unused (always 1)
FLAG_V = 0x40  # Overflow
FLAG_N = 0x80  # Negative


class CPU6502:
    def __init__(self, bus):
        self.bus = bus

        self.A = 0
        self.X = 0
        self.Y = 0
        self.PC = 0
        self.SP = 0xFD
        self.status = FLAG_U | FLAG_I

        self.cycles = 0

    # ================= BUS =================
    def read(self, addr):
        return self.bus.read(addr)

    def write(self, addr, value):
        self.bus.write(addr, value & 0xFF)

    # ================= FLAGS =================
    def set_flag(self, flag, value):
        if value:
            self.status |= flag
        else:
            self.status &= ~flag

    def get_flag(self, flag):
        return (self.status & flag) != 0

    def update_zn(self, value):
        self.set_flag(FLAG_Z, value == 0)
        self.set_flag(FLAG_N, value & 0x80)

    # ================= STACK =================
    def push(self, value):
        self.write(0x0100 + self.SP, value)
        self.SP = (self.SP - 1) & 0xFF

    def pop(self):
        self.SP = (self.SP + 1) & 0xFF
        return self.read(0x0100 + self.SP)

    # ================= RESET =================
    def reset(self):
        lo = self.read(0xFFFC)
        hi = self.read(0xFFFD)
        self.PC = (hi << 8) | lo
        self.SP = 0xFD
        self.status = FLAG_U | FLAG_I
        self.cycles = 7

    # ================= ADDRESSING =================
    def imm(self):
        addr = self.PC
        self.PC += 1
        return addr

    def zp(self):
        addr = self.read(self.PC)
        self.PC += 1
        return addr

    def abs(self):
        lo = self.read(self.PC)
        hi = self.read(self.PC + 1)
        self.PC += 2
        return (hi << 8) | lo

    # ================= INSTRUCTIONS =================
    def lda(self, addr):
        self.A = self.read(addr)
        self.update_zn(self.A)

    def sta(self, addr):
        self.write(addr, self.A)

    def jmp(self, addr):
        self.PC = addr

    def jsr(self, addr):
        pc = self.PC - 1
        self.push((pc >> 8) & 0xFF)
        self.push(pc & 0xFF)
        self.PC = addr

    def rts(self):
        lo = self.pop()
        hi = self.pop()
        self.PC = ((hi << 8) | lo) + 1

    # ================= EXECUTION =================
    def step(self):
        opcode = self.read(self.PC)
        self.PC += 1

        # --- LDA ---
        if opcode == 0xA9:  # Immediate
            self.lda(self.imm())
            self.cycles += 2

        elif opcode == 0xA5:  # Zero Page
            self.lda(self.zp())
            self.cycles += 3

        elif opcode == 0xAD:  # Absolute
            self.lda(self.abs())
            self.cycles += 4

        # --- STA ---
        elif opcode == 0x85:
            self.sta(self.zp())
            self.cycles += 3

        elif opcode == 0x8D:
            self.sta(self.abs())
            self.cycles += 4

        # --- JMP ---
        elif opcode == 0x4C:
            self.jmp(self.abs())
            self.cycles += 3

        # --- JSR / RTS ---
        elif opcode == 0x20:
            self.jsr(self.abs())
            self.cycles += 6

        elif opcode == 0x60:
            self.rts()
            self.cycles += 6

        # --- NOP ---
        elif opcode == 0xEA:
            self.cycles += 2

        # --- BRK ---
        elif opcode == 0x00:
            self.PC += 1
            self.set_flag(FLAG_B, True)
            self.push((self.PC >> 8) & 0xFF)
            self.push(self.PC & 0xFF)
            self.push(self.status)
            self.set_flag(FLAG_I, True)
            lo = self.read(0xFFFE)
            hi = self.read(0xFFFF)
            self.PC = (hi << 8) | lo
            self.cycles += 7

        else:
            raise Exception(f"Unknown opcode: {hex(opcode)}")
          
