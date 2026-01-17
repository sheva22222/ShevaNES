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
            self.P &= 0b11111101

        if value & 0x80:
            self.P |= 0b10000000
        else:
            self.P &= 0b01111111

    def step(self):
        opcode = self.memory[self.PC]
        self.PC += 1

        if opcode == 0xA9:  # LDA immediate
            value = self.memory[self.PC]
            self.PC += 1
            self.A = value
            self.update_zn(self.A)

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

            if self.P & 0b00000010:
                if offset & 0x80:
                    offset -= 256
                self.PC += offset
                
        elif opcode == 0x00:  # BRK
            raise StopIteration("BRK")
    
        elif opcode == 0x4C:  # JMP absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            self.PC = (high << 8) | low
    
        else:
            raise Exception(f"Unknown opcode {hex(opcode)}")
            
