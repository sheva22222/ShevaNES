from cpu import CPU

cpu = CPU()

program = [
    0xA2, 0x05,      # LDX #5
    0xCA,            # DEX
    0xD0, 0xFD       # BNE назад на DEX
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(cpu.X)
