from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x00,
    0xF0, 0x02,
    0xA9, 0x01,
    0xA9, 0x05,
    0x00,        # BRK
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(cpu.A)
