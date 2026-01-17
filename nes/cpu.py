class CPU:
    def __init__(self):
        self.A = 0
        self.X = 0
        self.Y = 0
        self.PC = 0x0000
        self.SP = 0xFD
        self.P = 0b00100000
        self.memory = [0] * 65536

    def load_program(self, program, start=0x8000):
        self.PC = start
        for i, byte in enumerate(program):
            self.memory[start + i] = byte

    def update_zn(self, value):
        if value == 0:
            self.P |= 0b00000010
        else:
    elif opcode == 0xE8:  # INX
        self.X = (self.X + 1) & 0xFF
        self.update_zn(self.X)

    elif opcode == 0x85:  # STA zeropage
        addr = self.memory[self.PC]
        self.PC += 1
        self.memory[addr] = self.A

    elif opcode == 0xF0:  # BEQ
        offset = self.memory[self.PC]
        self.PC += 1

        if self.P & 0b00000010:  # Z = 1
            if offset & 0x80:
                offset -= 256
            self.PC += offset

    else:
        raise Exception(f"Unknown opcode {hex(opcode)}")
