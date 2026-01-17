from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x03,   # LDA #3
    0xC9, 0x00,   # CMP #0
    0xD0, 0xFA,   # BNE -6 (назад к CMP)
    0x00
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))
print("C =", cpu.P & 1)
print("Z =", (cpu.P >> 1) & 1)
print("N =", (cpu.P >> 7) & 1)
print("P =", bin(cpu.P))

