from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0xFF,       # LDA #$FF  → N = 1
    0x30, 0x02,       # BMI +2 (должен сработать)
    0xA9, 0x01,       # LDA #$01 (пропуск)
    0xA9, 0x05        # LDA #$05
]

cpu.load_program(program)
for _ in range(10):
    cpu.step()

print(hex(cpu.A))
print("N =", (cpu.P >> 7) & 1)
