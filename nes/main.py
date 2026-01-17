from cpu import CPU

cpu = CPU()

program = [
    0xE8,            # INX
    0x4C, 0x00, 0x80 # JMP $8000
]

cpu.load_program(program)

try:
    for _ in range(10):
    cpu.step()

print(cpu.X)

