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
for _ in range(10):
    cpu.step()

print(hex(cpu.A))
print("C =", cpu.P & 1)


