from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x05,
    0xC9, 0x03,   # A >= 3 → C = 1
    0xB0, 0x02,   # BCS +2
    0xA9, 0x01,   # пропуск
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

