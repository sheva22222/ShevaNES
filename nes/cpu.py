class CPU:
    FLAG_BITS = {
        'C': 0,
        'Z': 1,
        'I': 2,
        'D': 3,
        'B': 4,
        'V': 6,
        'N': 7,
    }

    def __init__(self):
        self.A = 0
        self.X = 0
        self.Y = 0
        self.P = 0x24
        self.PC = 0
        self.SP = 0xFD
        self.memory = [0] * 0x10000

    def set_flag(self, flag, value):
        bit = self.FLAG_BITS[flag]
        if value:
            self.P |= (1 << bit)
        else:
            self.P &= ~(1 << bit)

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
        self.P = 0b00100100

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

    def INC(self, addr):
        value = (self.memory[addr] + 1) & 0xFF
        self.memory[addr] = value
        self.update_zn(value)

    def fetch_byte(self):
        value = self.memory[self.PC]
        self.PC = (self.PC + 1) & 0xFFFF
        return value

    def fetch_word(self):
        low = self.fetch_byte()
        high = self.fetch_byte()
        return (high << 8) | low

    def addr_zeropage(self):
        return self.fetch_byte()

    def addr_zeropage_x(self):
        return (self.fetch_byte() + self.X) & 0xFF

    def addr_zeropage_y(self):
        return (self.fetch_byte() + self.Y) & 0xFF

    def addr_absolute(self):
        return self.fetch_word()

    def addr_absolute_x(self):
        return (self.fetch_word() + self.X) & 0xFFFF

    def addr_absolute_y(self):
        return (self.fetch_word() + self.Y) & 0xFFFF

    def addr_indirect_x(self):
        zp = (self.fetch_byte() + self.X) & 0xFF
        low = self.memory[zp]
        high = self.memory[(zp + 1) & 0xFF]
        return (high << 8) | low

    def addr_indirect_y(self):
        zp = self.memory[self.PC]
        self.PC += 1
        low = self.memory[zp]
        high = self.memory[(zp + 1) & 0xFF]
        return ((high << 8) | low) + self.Y & 0xFFFF

    def addr_jmp_indirect(self):
        ptr = self.fetch_word()
        low = self.memory[ptr]
        if (ptr & 0x00FF) == 0x00FF:
            high = self.memory[ptr & 0xFF00]
        else:
            high = self.memory[ptr + 1]
        return (high << 8) | low

    def set_ZN(self, v):
        self.P = (self.P & ~0b10000010) | \
                 (0b10 if v == 0 else 0) | \
                 (0b10000000 if v & 0x80 else 0)

    def compare(self, reg, value):
        result = (reg - value) & 0xFF
        self.set_flag_C(reg >= value)
        self.set_flag_Z(result == 0)
        self.set_flag_N(result & 0x80)

    def set_zn(self, value):
        self.set_flag('Z', value == 0)
        self.set_flag('N', value & 0x80)

    def addr_zp_x_indirect(self):
        zp = self.memory[self.PC]
        self.PC += 1
        lo = self.memory[(zp + self.X) & 0xFF]
        hi = self.memory[(zp + self.X + 1) & 0xFF]
        return lo | (hi << 8)

    def addr_zp_x(self):
        zp = self.memory[self.PC]
        self.PC += 1
        lo = self.memory[(zp + self.X) & 0xFF]
        hi = self.memory[(zp + self.X + 1) & 0xFF]
        return lo | (hi << 8)

    def sbc(self, value):
        self.adc(value ^ 0xFF)

    def adc(self, value):
        carry = self.P & 1
        result = self.A + value + carry

        self.P = (self.P & ~1) | (1 if result > 0xFF else 0)
        self.P = (self.P & ~2) | (1 if (result & 0xFF) == 0 else 0)
        self.P = (self.P & ~0x80) | (result & 0x80)

        self.A = result & 0xFF

    def get_flag(self, flag):
        return (self.P >> self.FLAG_BITS[flag]) & 1
    
    def step(self):
        pc_before = self.PC
        opcode = self.fetch_byte()

        print(f"PC={pc_before:04X} OP={opcode:02X}")

        if opcode == 0xA9:  # LDA #imm
            value = self.read(self.PC)
            self.PC += 1
            self.A = value
            
        elif opcode == 0xE8:  # INX
            self.X = (self.X + 1) & 0xFF
            self.update_zn(self.X)

        elif opcode == 0x85:  # STA zeropage
            addr = self.fetch_byte()
            self.memory[addr] = self.A

        elif opcode == 0x86:  # STX zeropage
            addr = self.fetch_byte()
            self.memory[addr] = self.X

        elif opcode == 0xF0:
            offset = self.fetch_byte()
            if self.get_flag('Z'):
                if offset & 0x80:
                    offset -= 0x100
                self.PC = (self.PC + offset) & 0xFFFF
        
        elif opcode == 0xD0:  # BNE
            offset = self.fetch_byte()

            if ((self.P >> 1) & 1) == 0:  # Z == 0
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0xB0:  # BCS
            offset = self.fetch_byte()

            if self.P & 1:  # C == 1
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x00:  # BRK какаха пипити
            self.PC = (self.PC + 1) & 0xFFFF

            # push PC high
            self.memory[0x0100 + self.SP] = (self.PC >> 8) & 0xFF
            self.SP = (self.SP - 1) & 0xFF

            # push PC low
            self.memory[0x0100 + self.SP] = self.PC & 0xFF
            self.SP = (self.SP - 1) & 0xFF

            # push P with B=1, U=1
            p = self.P | 0b00010000 | 0b00100000
            self.memory[0x0100 + self.SP] = p
            self.SP = (self.SP - 1) & 0xFF

            # set I
            self.P |= 0b00000100

            # load IRQ/BRK vector
            low = self.memory[0xFFFE]
            high = self.memory[0xFFFF]
            self.PC = (high << 8) | low

            raise StopIteration("BRK")

        elif opcode == 0xA2:  # LDX #imm
            value = self.fetch_byte()
            self.X = value
            self.update_zn(self.X)

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
            value = self.fetch_byte()
            self.A = value
            self.update_zn(self.A)

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

            low = self.fetch_byte()
            high = self.fetch_byte()
            return_addr = self.PC - 1

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
            value = self.fetch_byte()
            result = (self.A - value) & 0xFF

            # Carry
            if self.A >= value:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            self.update_zn(result)

        elif opcode == 0x90:  # BCC
            offset = self.fetch_byte()

            if not (self.P & 1):  # C == 0
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x30:  # BMI
            offset = self.fetch_byte()

            if self.P & 0b10000000:  # N == 1
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x10:  # BPL
            offset = self.fetch_byte()

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
            value = self.fetch_byte()
            self.A = value
            self.update_zn(self.A)

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
            addr = self.fetch_byte()
            self.memory[addr] = self.A

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
            value = self.fetch_byte()
            self.A = value
            self.update_zn(self.A)

            self.A = self.A & value
            self.update_zn(self.A)

        elif opcode == 0x25:  # AND zeropage
            addr = self.fetch_byte()
            self.memory[addr] = self.A

            self.A = self.A & self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0x09:  # ORA immediate
            value = self.memory[self.PC]
            self.PC += 1
            self.A |= value
            self.update_zn(self.A)

        elif opcode == 0x49:  # EOR immediate
            value = self.fetch_byte()
            self.A = value
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

        elif opcode == 0x2A:  # ROL A
            old_c = self.P & 1
            new_c = (self.A >> 7) & 1

            if new_c:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            self.A = ((self.A << 1) & 0xFF) | old_c
            self.update_zn(self.A)

        elif opcode == 0x6A:  # ROR A
            old_c = self.P & 1
            new_c = self.A & 1

            if new_c:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            self.A = (self.A >> 1) | (old_c << 7)
            self.update_zn(self.A)

        elif opcode == 0xE6:  # INC zeropage
            addr = self.fetch_byte()
            self.memory[addr] = self.A

            value = (self.memory[addr] + 1) & 0xFF
            self.memory[addr] = value

            self.update_zn(value)

        elif opcode == 0xF6:  # INC zeropage,X
            addr = (self.fetch_byte() + self.X) & 0xFF
            self.INC(addr)

        elif opcode == 0xEE:  # INC absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            self.PC += 2

            addr = (high << 8) | low

            value = (self.memory[addr] + 1) & 0xFF
            self.memory[addr] = value

            self.update_zn(value)

        elif opcode == 0xFE:  # INC absolute,X
            addr = (self.fetch_word() + self.X) & 0xFFFF
            self.INC(addr)

        elif opcode == 0xC6:  # DEC zeropage
            addr = self.fetch_byte()
            self.memory[addr] = self.A

            value = (self.memory[addr] - 1) & 0xFF
            self.memory[addr] = value

            self.update_zn(value)

        elif opcode == 0xD6:  # DEC zeropage,X
            addr = self.fetch_byte()
            self.memory[addr] = self.A

            value = (self.memory[addr] - 1) & 0xFF
            self.memory[addr] = value

            self.update_zn(value)

        elif opcode == 0xCE:  # DEC absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            addr = (high << 8) | low
            self.PC += 2

            value = (self.memory[addr] - 1) & 0xFF
            self.memory[addr] = value

            self.update_zn(value)

        elif opcode == 0xDE:  # DEC absolute,X
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            addr = ((high << 8) | low) + self.X
            addr &= 0xFFFF
            self.PC += 2

            value = (self.memory[addr] - 1) & 0xFF
            self.memory[addr] = value

            self.update_zn(value)

        elif opcode == 0x70:  # BVS
            offset = self.fetch_byte()

            if self.P & 0b01000000:  # V == 1
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x50:  # BVC
            offset = self.fetch_byte()

            if not (self.P & 0b01000000):  # V == 0
                if offset & 0x80:
                    offset -= 0x100
                self.PC += offset

        elif opcode == 0x2D:  # AND absolute
            low = self.memory[self.PC]
            high = self.memory[self.PC + 1]
            self.PC += 2

            addr = (high << 8) | low
            self.A = self.A & self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0xDB:  #чат попати дурак
            pass

        elif opcode in (
            0xDB, 0xD3, 0xCF, 0xC7, 0xD7, 0xDF,
            0xE3, 0xE7, 0xEB, 0xF3, 0xF7, 0xFB,
            0x03, 0x07, 0x0B, 0x0F,
            0x13, 0x17, 0x1B, 0x1F,
            0x23, 0x27, 0x2B, 0x2F,
            0x33, 0x37, 0x3B, 0x3F
        ):
            pass

        elif opcode == 0xF8:  # SED
            self.P |= 0b00001000  # D = 1

        elif opcode == 0xD8:  # CLD
            self.P &= ~0b00001000

        elif opcode == 0xA0:  # LDY #imm
            value = self.fetch_byte()
            self.A = value
            self.update_zn(self.A)

        elif opcode == 0xC0:  # CPY #imm
            value = self.fetch_byte()
            self.A = value
            self.update_zn(self.A)

            result = (self.Y - value) & 0xFF

            # Carry
            if self.Y >= value:
                self.P |= 0b00000001
            else:
                self.P &= ~0b00000001

            # Zero
            if result == 0:
                self.P |= 0b00000010
            else:
                self.P &= ~0b00000010

            # Negative
            if result & 0x80:
                self.P |= 0b10000000
            else:
                self.P &= ~0b10000000

        elif opcode == 0xE0:  # CPX #imm
            value = self.fetch_byte()
            self.A = value
            self.update_zn(self.A)

            result = (self.X - value) & 0xFF

            # Carry
            if self.X >= value:
                self.P |= 0b00000001
            else:
                self.P &= ~0b00000001

            # Zero
            if result == 0:
                self.P |= 0b00000010
            else:
                self.P &= ~0b00000010

            # Negative
            if result & 0x80:
                self.P |= 0b10000000
            else:
                self.P &= ~0b10000000

        elif opcode == 0x31:  # AND (zp),Y
            zp = self.fetch_byte()

            low = self.memory[zp]
            high = self.memory[(zp + 1) & 0xFF]
            addr = ((high << 8) | low) + self.Y
            addr &= 0xFFFF

            self.A &= self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0x84:  # STY zeropage
            addr = self.fetch_byte()
            self.memory[addr] = self.A

        elif opcode == 0xF9:  # SBC absolute,Y
            addr = (self.fetch_word() + self.Y) & 0xFFFF
            value = self.memory[addr]

            carry = self.P & 1
            result = self.A - value - (1 - carry)

            # C (no borrow)
            if result >= 0:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            result8 = result & 0xFF

            # V
            if ((self.A ^ result8) & (self.A ^ value) & 0x80):
                self.P |= 0b01000000
            else:
                self.P &= 0b10111111

            self.A = result8
            self.update_zn(self.A)

        elif opcode == 0x47:  # SRE zeropage (illegal)
            addr = self.fetch_byte()
            value = self.memory[addr]

            # LSR
            carry = value & 1
            value = (value >> 1) & 0xFF
            self.memory[addr] = value

            if carry:
                self.P |= 0b00000001
            else:
                self.P &= 0b11111110

            # EOR
            self.A ^= value
            self.update_zn(self.A)

        elif opcode == 0x28:  # PLP
            self.SP = (self.SP + 1) & 0xFF
            self.P = self.memory[0x0100 + self.SP]

            # B = 0, U = 1
            self.P &= 0b11101111
            self.P |= 0b00100000

        elif opcode == 0xC8:  # INY
            self.Y = (self.Y + 1) & 0xFF
            self.update_zn(self.Y)

        elif opcode == 0x88:  # DEY
            self.Y = (self.Y - 1) & 0xFF
            self.update_zn(self.Y)

        elif opcode == 0xA8:  # TAY
            self.Y = self.A
            self.update_zn(self.Y)

        elif opcode == 0xAA:  # TAX
            self.X = self.A
            self.update_zn(self.X)

        elif opcode == 0x8A:  # TXA
            self.A = self.X
            self.update_zn(self.A)

        elif opcode == 0x98:  # TYA
            self.A = self.Y
            self.update_zn(self.A)

        elif opcode == 0xBA:  # TSX
            self.X = self.SP
            self.set_ZN(self.X)
    
        elif opcode == 0x9A:  # TXS
            self.SP = self.X

        elif opcode == 0x8E:  # STX absolute
            lo = self.memory[self.PC]
            hi = self.memory[self.PC + 1]
            addr = (hi << 8) | lo
            self.PC += 2
            self.memory[addr] = self.X

        elif opcode == 0xAE:  # LDX absolute
            lo = self.memory[self.PC]
            hi = self.memory[self.PC + 1]
            self.PC += 2

            addr = lo | (hi << 8)
            self.X = self.memory[addr]
            self.set_ZN(self.X)

        elif opcode == 0xAD:  # LDA absolute
            lo = self.memory[self.PC]
            hi = self.memory[self.PC + 1]
            self.PC += 2

            addr = lo | (hi << 8)
            self.A = self.memory[addr]
            self.set_ZN(self.A)

        elif opcode == 0xA5:  # LDA zeropage
            addr = self.fetch_byte()
            self.memory[addr] = self.A

            self.A = self.memory[addr]
            self.set_ZN(self.A)

        elif opcode == 0xA1:  # LDA (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            addr_lo = self.memory[(zp + self.X) & 0xFF]
            addr_hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = addr_lo | (addr_hi << 8)

            self.A = self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0xB1:  # LDA (zp),Y
            zp = self.fetch_byte()

            lo = self.memory[zp]
            hi = self.memory[(zp + 1) & 0xFF]
            addr = ((lo | (hi << 8)) + self.Y) & 0xFFFF

            self.A = self.memory[addr]
            self.set_ZN(self.A)

        elif opcode == 0x81:  # STA (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            addr_lo = self.memory[(zp + self.X) & 0xFF]
            addr_hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = addr_lo | (addr_hi << 8)

            self.memory[addr] = self.A

        elif opcode == 0x01:  # ORA (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            addr_lo = self.memory[(zp + self.X) & 0xFF]
            addr_hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = addr_lo | (addr_hi << 8)

            self.A |= self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0x21:  # AND (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            addr_lo = self.memory[(zp + self.X) & 0xFF]
            addr_hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = addr_lo | (addr_hi << 8)

            self.A &= self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0x41:  # EOR (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            addr_lo = self.memory[(zp + self.X) & 0xFF]
            addr_hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = addr_lo | (addr_hi << 8)

            self.A ^= self.memory[addr]
            self.update_zn(self.A)

        elif opcode == 0x61:  # ADC (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            addr_lo = self.memory[(zp + self.X) & 0xFF]
            addr_hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = addr_lo | (addr_hi << 8)

            value = self.memory[addr]
            carry = self.P & 1

            result = self.A + value + carry

            # Carry
            if result > 0xFF:
                self.P |= 0x01
            else:
                self.P &= ~0x01

            # Overflow
            if (~(self.A ^ value) & (self.A ^ result)) & 0x80:
                self.P |= 0x40
            else:
                self.P &= ~0x40

            self.A = result & 0xFF
            self.update_zn(self.A)

        elif opcode == 0xC1:  # CMP (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            addr_lo = self.memory[(zp + self.X) & 0xFF]
            addr_hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = addr_lo | (addr_hi << 8)

            value = self.memory[addr]

            result = (self.A - value) & 0x1FF

            # Carry: A >= value
            if self.A >= value:
                self.P |= 0x01
            else:
                self.P &= ~0x01

            # Zero
            if (result & 0xFF) == 0:
                self.P |= 0x02
            else:
                self.P &= ~0x02

            # Negative
            if result & 0x80:
                self.P |= 0x80
            else:
                self.P &= ~0x80

        elif opcode == 0xE1:  # SBC (zp,X)
            zp = self.memory[self.PC]
            self.PC += 1

            lo = self.memory[(zp + self.X) & 0xFF]
            hi = self.memory[(zp + self.X + 1) & 0xFF]
            addr = lo | (hi << 8)

            value = self.memory[addr]

            carry = 1 if (self.P & 0x01) else 0
            result = self.A - value - (1 - carry)

            # Overflow
            if ((self.A ^ value) & 0x80) and ((self.A ^ result) & 0x80):
                self.P |= 0x40
            else:
                self.P &= ~0x40

            # Carry (нет заёма)
            if result >= 0:
                self.P |= 0x01
            else:
                self.P &= ~0x01

            self.A = result & 0xFF

            # Zero
            if self.A == 0:
                self.P |= 0x02
            else:
                self.P &= ~0x02

            # Negative
            if self.A & 0x80:
                self.P |= 0x80
            else:
                self.P &= ~0x80

        elif opcode == 0xA4:  # LDY zeropage
            addr = self.memory[self.PC]
            self.PC += 1

            self.Y = self.memory[addr]
            self.update_zn(self.Y)

        elif opcode == 0xA6:  # LDX zeropage
            addr = self.memory[self.PC]
            self.PC += 1

            self.X = self.memory[addr]
            self.update_zn(self.X)

        elif opcode == 0x05:  # ORA zeropage
            addr = self.memory[self.PC]
            self.PC += 1

            self.A |= self.memory[addr]
            self.A &= 0xFF

            self.update_zn(self.A)

        elif opcode == 0x45:  # EOR zeropage
            addr = self.memory[self.PC]
            self.PC += 1

            self.A ^= self.memory[addr]
            self.A &= 0xFF

            self.update_zn(self.A)

        elif opcode == 0x65:  # ADC zeropage
            addr = self.memory[self.PC]
            self.PC += 1
            value = self.memory[addr]
            self.adc(value)

        elif opcode == 0xC5:  # CMP zp
            zp = self.memory[self.PC]
            self.PC += 1
            value = self.memory[zp]

            result = self.A - value

            self.set_flag('C', self.A >= value)
            self.set_flag('Z', (result & 0xFF) == 0)
            self.set_flag('N', result & 0x80)

        elif opcode == 0xE9:  # SBC immediate
            value = self.memory[self.PC]
            self.PC += 1
            self.sbc(value)

        elif opcode == 0xE5:  # SBC zeropage
            addr = self.memory[self.PC]
            self.PC += 1
            value = self.memory[addr]
            self.sbc(value)

        elif opcode == 0xF5:  # SBC zeropage,X
            zp = (self.memory[self.PC] + self.X) & 0xFF
            self.PC += 1
            self.sbc(self.memory[zp])

        elif opcode == 0xED:  # SBC absolute
            lo = self.memory[self.PC]
            hi = self.memory[self.PC + 1]
            self.PC += 2
            addr = (hi << 8) | lo
            self.sbc(self.memory[addr])

        elif opcode == 0xFD:  # SBC absolute,X
            lo = self.memory[self.PC]
            hi = self.memory[self.PC + 1]
            self.PC += 2
            addr = ((hi << 8) | lo) + self.X
            self.sbc(self.memory[addr & 0xFFFF])

        elif opcode == 0xF9:  # SBC absolute,Y
            lo = self.memory[self.PC]
            hi = self.memory[self.PC + 1]
            self.PC += 2
            addr = ((hi << 8) | lo) + self.Y
            self.sbc(self.memory[addr & 0xFFFF])

        elif opcode == 0xE1:  # SBC (zp,X)
            zp = (self.memory[self.PC] + self.X) & 0xFF
            self.PC += 1
            lo = self.memory[zp]
            hi = self.memory[(zp + 1) & 0xFF]
            addr = (hi << 8) | lo
            self.sbc(self.memory[addr])

        elif opcode == 0xF1:  # SBC (zp),Y
            zp = self.memory[self.PC]
            self.PC += 1
            lo = self.memory[zp]
            hi = self.memory[(zp + 1) & 0xFF]
            addr = ((hi << 8) | lo) + self.Y
            self.sbc(self.memory[addr & 0xFFFF])

        elif opcode == 0xE4:  # CPX zp
            zp = self.memory[self.PC]
            self.PC += 1
            value = self.memory[zp]

            result = self.X - value

            self.set_flag('C', self.X >= value)
            self.set_flag('Z', (result & 0xFF) == 0)
            self.set_flag('N', result & 0x80)

        elif opcode == 0xC4:  # CPY zp
            zp = self.memory[self.PC]
            self.PC += 1
            value = self.memory[zp]

            result = self.Y - value

            self.set_flag('C', self.Y >= value)
            self.set_flag('Z', (result & 0xFF) == 0)
            self.set_flag('N', result & 0x80)

        elif opcode == 0x46:  # LSR zeropage
            addr = self.fetch_byte()
            value = self.read(addr)

            self.set_flag('C', value & 0x01)

            value = (value >> 1) & 0xFF
            self.write(addr, value)

            self.set_flag('Z', value == 0)
            self.set_flag('N', False)
        
        else:
            raise Exception(f"Unknown opcode {hex(opcode)}")
            
