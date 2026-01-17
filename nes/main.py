from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x2A,        # LDA #42
    0x8D, 0x00, 0x02,  # STA $0200
    0xA9, 0x00,        # LDA #0
    0xA9, 0x2A         # LDA #42
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(cpu.A)
print(cpu.memory[0x0200])
