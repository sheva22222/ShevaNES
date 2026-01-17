from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x00,
    0xF0, 0x02,
    0xA9, 0x01,
    0xA9, 0x05,
]

cpu.load_program(program)

for _ in range(4):
    cpu.step()

print(cpu.A)
