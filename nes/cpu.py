class CPU:
    def __init__(self):
        self.P = 0b00100000  # флаг U всегда = 1
        self.A = 0
        self.X = 0
        self.PC = 0x8000
        self.SP = 0xFD

        self.memory = [0] * 65536  # ← ВОТ ЭТО ОБЯЗАТЕЛЬНО

    def load_program(self, program, start=0x8000):
        for i, byte in enumerate(program):
            self.memory[start + i] = byte
        self.PC = start

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

            if (self.P >> 1) & 1:  # Z flag
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0xD0:  # BNE
            offset = self.memory[self.PC]
            self.PC += 1

            if ((self.P >> 1) & 1) == 0:  # Z == 0
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0xB0:  # BCS
            offset = self.memory[self.PC]
            self.PC += 1

            if self.P & 1:  # C == 1
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x00:  # BRK
            raise StopIteration("BRK")

        elif opcode == 0xA2:  # LDX immediate
            self.X = self.memory[self.PC]
            self.PC += 1

        elif opcode == 0xCA:  # DEX
            self.X = (self.X - 1) & 0xFF
            self.Z = 1 if self.X == 0 else 0

        elif opcode == 0x8D:  # STA absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            addr = (high << 8) | low
            self.memory[addr] = self.A
            self.PC += 2

        elif opcode == 0x69:  # ADC immediate
            value = self.memory[self.PC]
            self.PC += 1

            result = self.A + value + self.C
            self.C = 1 if result > 0xFF else 0

            result8 = result & 0xFF

            self.V = 1 if (~(self.A ^ value) & (self.A ^ result8) & 0x80) else 0
            self.A = result8

            self.Z = 1 if self.A == 0 else 0
            self.N = 1 if self.A & 0x80 else 0

        elif opcode == 0x48:  # PHA
            self.memory[0x0100 + self.SP] = self.A
            self.SP = (self.SP - 1) & 0xFF

        elif opcode == 0x68:  # PLA
            self.SP = (self.SP + 1) & 0xFF
            self.A = self.memory[0x0100 + self.SP]
            self.Z = 1 if self.A == 0 else 0

        elif opcode == 0x20:  # JSR absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]

            return_addr = self.PC + 1  # КРИТИЧНО

            # push high
            self.memory[0x0100 + self.SP] = (return_addr >> 8) & 0xFF
            self.SP = (self.SP - 1) & 0xFF

            # push low
            self.memory[0x0100 + self.SP] = return_addr & 0xFF
            self.SP = (self.SP - 1) & 0xFF

            self.PC = (high << 8) | low

        elif opcode == 0x4C:  # JMP absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            self.PC = (high << 8) | low

        elif opcode == 0x60:  # RTS
            self.SP = (self.SP + 1) & 0xFF
            low = self.memory[0x0100 + self.SP]

            self.SP = (self.SP + 1) & 0xFF
            high = self.memory[0x0100 + self.SP]

            self.PC = ((high << 8) | low) + 1

        elif opcode == 0xC9:  # CMP immediate
            value = self.memory[self.PC]
            self.PC += 1

            result = (self.A - value) & 0xFF

            if self.A >= value:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            self.update_zn(result)

        elif opcode == 0x90:  # BCC
            offset = self.memory[self.PC]
            self.PC += 1

            if not (self.P & 1):  # C == 0
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x30:  # BMI
            offset = self.memory[self.PC]
            self.PC += 1

            if self.P & 0b10000000:  # N == 1
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x10:  # BPL
            offset = self.memory[self.PC]
            self.PC += 1

            if not (self.P & 0b10000000):  # N == 0
               if offset & 0x80:
                   offset -= 0x100
               self.PC += offset
        
        else:
            raise Exception(f"Unknown opcode {hex(opcode)}")
            
