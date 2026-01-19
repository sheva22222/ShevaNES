class CPU:
    def __init__(self):
        self.I = 0
        self.P = 0b00100100  # флаг U всегда = 1
        self.A = 0
        self.X = 0
        self.SP = 0xFD

        self.memory = [0] * 65536  # ← ВОТ ЭТО ОБЯЗАТЕЛЬНО

    def load_program(self, program, start=0x8000):
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

    def reset(self):
        low = self.memory[0xFFFC]
        high = self.memory[0xFFFD]
        self.PC = (high << 8) | low

        self.SP = 0xFD
        self.P = 0b00100000

    def set_I(self, value):
        if value:
            self.P |= 0b00000100
            self.I = 1
        else:
            self.P &= 0b11111011
            self.I = 0

    def irq(self):
        # если I = 1, IRQ игнорируется
        if self.P & 0b00000100:
            return

        # push PC (high)
        self.memory[0x0100 + self.SP] = (self.PC >> 8) & 0xFF
        self.SP = (self.SP - 1) & 0xFF

        # push PC (low)
        self.memory[0x0100 + self.SP] = self.PC & 0xFF
        self.SP = (self.SP - 1) & 0xFF

        # push P (B = 0, U = 1)
        p = self.P & 0b11101111
        p |= 0b00100000

        self.memory[0x0100 + self.SP] = p
        self.SP = (self.SP - 1) & 0xFF

        # I = 1
        self.P |= 0b00000100

        # load IRQ vector
        low = self.memory[0xFFFE]
        high = self.memory[0xFFFF]
        self.PC = (high << 8) | low

    def nmi(self):
        # push PC high
        self.memory[0x0100 + self.SP] = (self.PC >> 8) & 0xFF
        self.SP = (self.SP - 1) & 0xFF

        # push PC low
        self.memory[0x0100 + self.SP] = self.PC & 0xFF
        self.SP = (self.SP - 1) & 0xFF

        # push P (B = 0, U = 1)
        p = self.P & 0b11101111   # B = 0
        p |= 0b00100000          # U = 1

        self.memory[0x0100 + self.SP] = p
        self.SP = (self.SP - 1) & 0xFF

        # I = 1
        self.P |= 0b00000100

        # load NMI vector
        low = self.memory[0xFFFA]
        high = self.memory[0xFFFB]
        self.PC = (high << 8) | low
        
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

        elif opcode == 0x00:  # BRK нилагична так дилать попати

            self.PC += 1

            # push PC high
            self.memory[0x0100 + self.SP] = (self.PC >> 8) & 0xFF
            self.SP = (self.SP - 1) & 0xFF

            # push PC low
            self.memory[0x0100 + self.SP] = self.PC & 0xFF
            self.SP = (self.SP - 1) & 0xFF

            # push P (B=1, U=1)
            p = self.P | 0b00010000  # B = 1
            p |= 0b00100000          # U = 1
            self.memory[0x0100 + self.SP] = p
            self.SP = (self.SP - 1) & 0xFF

            # I = 1
            self.P |= 0b00000100

            # load IRQ/BRK vector
            low = self.memory[0xFFFE]
            high = self.memory[0xFFFF]
            self.PC = (high << 8) | low

            raise StopIteration("BRK")

        elif opcode == 0xA2:  # LDX immediate
            self.X = self.memory[self.PC]
            self.PC += 1

        elif opcode == 0xCA:  # DEX
            self.X = (self.X - 1) & 0xFF
            self.update_zn(self.X)

        elif opcode == 0x8D:  # STA absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            addr = (high << 8) | low
            self.memory[addr] = self.A
            self.PC += 2

        elif opcode == 0x69:  # ADC immediate
            value = self.memory[self.PC]
            self.PC += 1

            carry = self.P & 1
            result = self.A + value + carry

            # C
            if result > 0xFF:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            result8 = result & 0xFF

            # V
            if (~(self.A ^ value) & (self.A ^ result8) & 0x80):
                self.P |= 0b01000000
            else:
                self.P &= 0b10111111

            self.A = result8
            self.update_zn(self.A)

        elif opcode == 0x48:  # PHA
            self.memory[0x0100 + self.SP] = self.A
            self.SP = (self.SP - 1) & 0xFF

        elif opcode == 0x68:  # PLA
            self.SP = (self.SP + 1) & 0xFF
            self.A = self.memory[0x0100 + self.SP]
            self.update_zn(self.A)

        elif opcode == 0x20:  # JSR absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]

            return_addr = self.PC - 1  # КРИТИЧНО

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

        elif opcode == 0x6C:  # JMP indirect (with 6502 bug)
            ptr_low = self.memory[self.PC]
            ptr_high = self.memory[self.PC + 1]
            ptr = (ptr_high << 8) | ptr_low

            # 6502 page boundary bug
            low = self.memory[ptr]
            if (ptr & 0x00FF) == 0x00FF:
                high = self.memory[ptr & 0xFF00]
            else:
                high = self.memory[ptr + 1]

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

        elif opcode == 0x40:  # RTI чат гпт гамно мале поставило после этой строчки комент
            self.SP = (self.SP + 1) & 0xFF
            self.P = self.memory[0x0100 + self.SP]
            self.P &= 0b11101111  # B = 0
            self.P |= 0b00100000  # U = 1

            # pull PC low
            self.SP = (self.SP + 1) & 0xFF
            low = self.memory[0x0100 + self.SP]

            # pull PC high
            self.SP = (self.SP + 1) & 0xFF
            high = self.memory[0x0100 + self.SP]

            self.PC = (high << 8) | low

        elif opcode == 0xEA:  # NOP
            pass

        elif opcode == 0x18:  # CLC
            self.P &= 0b11111110

        elif opcode == 0x38:  # SEC
            self.P |= 0b00000001

        elif opcode == 0x58:  # CLI
            self.P &= 0b11111011
            self.I = 0

        elif opcode == 0x78:  # SEI
            self.P |= 0b00000100
            self.I = 1

        elif opcode == 0xB8:  # CLV
            self.P &= 0b10111111

        elif opcode == 0x08:  # PHP
            p = (self.P & 0b11101111) | 0b00110000
            self.memory[0x0100 + self.SP] = p
            self.SP = (self.SP - 1) & 0xFF

        elif opcode == 0xE9:  # SBC immediate
            value = self.memory[self.PC]
            self.PC += 1

            carry = self.P & 1
            result = self.A - value - (1 - carry)

            # C flag (no borrow)
            if result >= 0:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            result8 = result & 0xFF

            # V flag
            if ((self.A ^ result8) & (self.A ^ value) & 0x80):
                self.P |= 0b01000000
            else:
                self.P &= 0b10111111

            self.A = result8
            self.update_zn(self.A)

        elif opcode == 0x24:  # BIT zeropage
            addr = self.memory[self.PC]
            self.PC += 1

            value = self.memory[addr]
            result = self.A & value

            # Z
            if result == 0:
                self.P |= 0b00000010
            else:
                self.P &= 0b11111101

            # N (bit 7 of memory)
            if value & 0x80:
                self.P |= 0b10000000
            else:
                self.P &= 0b01111111

            # V (bit 6 of memory)
            if value & 0x40:
                self.P |= 0b01000000
            else:
                self.P &= 0b10111111

        elif opcode == 0x29:  # AND immediate
            value = self.memory[self.PC]
            self.PC += 1

            self.A = self.A & value
            self.update_zn(self.A)

        elif opcode == 0x25:  # AND zeropage
            addr = self.memory[self.PC]
            self.PC += 1

            self.A = self.A & self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0x09:  # ORA immediate
            value = self.memory[self.PC]
            self.PC += 1
            self.A |= value
            self.update_zn(self.A)

        elif opcode == 0x49:  # EOR immediate
            value = self.memory[self.PC]
            self.PC += 1
            self.A ^= value
            self.update_zn(self.A)

        elif opcode == 0x0A:  # ASL A
            carry = (self.A >> 7) & 1

            if carry:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            self.A = (self.A << 1) & 0xFF
            self.update_zn(self.A)

        elif opcode == 0x4A:  # LSR A
            carry = self.A & 1

            if carry:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            self.A = (self.A >> 1) & 0xFF
            self.update_zn(self.A)    
        
        else:
            raise Exception(f"Unknown opcode {hex(opcode)}")
            
