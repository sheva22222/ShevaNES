from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0xFF,  # LDA #$FF
    0x30, 0x02,  # BMI +2
    0xA9, 0x01,  # LDA #$01
    0xA9, 0x05,  # LDA #$05
    0x00         # BRK
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))
print("N =", (cpu.P >> 7) & 1)
