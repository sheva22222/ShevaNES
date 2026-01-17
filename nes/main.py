from cpu import CPU

cpu = CPU()

program = [
    0xA9, 42,   # LDA #42
    0x48,       # PHA
    0xA9, 0,    # LDA #0
    0x68        # PLA
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(cpu.A)
