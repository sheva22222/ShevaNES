from cpu import CPU

cpu = CPU()

program = [
    0xE8,  # INX
    0xE8,  # INX
    0xE8,  # INX
]

cpu.load_program(program)

for _ in range(3):
    cpu.step()

print(cpu.X)  # должно быть 3
