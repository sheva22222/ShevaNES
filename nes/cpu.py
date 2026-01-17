class CPU:
    def __init__(self):
        self.A = 0
        self.X = 0
        self.Y = 0
        self.PC = 0x0000
        self.SP = 0xFD
        self.memory = [0] * 65536

    def load_program(self, program, start=0x8000):
        self.PC = start
        for i, byte in enumerate(program):
            self.memory[start + i] = byte

    def step(self):
        opcode = self.memory[self.PC]
        self.PC += 1

        if opcode == 0xA9:  # LDA immediate
            value = self.memory[self.PC]
            self.PC += 1
            self.A = value

        elif opcode == 0xE8:  # INX
            self.X = (self.X + 1) & 0xFF

        else:
            raise Exception(f"Unknown opcode {hex(opcode)}")
