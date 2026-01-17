from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x00,  # LDA #0 → Z = 1
    0xF0, 0x02,  # BEQ +2
    0xA9, 0x01,  # (пропускается)
    0xA9, 0x05,  # A = 5
]

cpu.load_program(program)

for _ in range(4):
    cpu.step()

print(cpu.A)

