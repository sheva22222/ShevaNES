from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x03,       # LDA #$03
    0xC9, 0x05,       # CMP #$05  → C = 0
    0x90, 0x02,       # BCC +2 (должен сработать)
    0xA9, 0x01,       # LDA #$01 (пропуск)
    0xA9, 0x05        # LDA #$05
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

