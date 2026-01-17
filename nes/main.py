from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x50,   # LDA #80
    0x69, 0x50    # ADC #80  → 160 (переполнение знака)
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))
print(cpu.V)
print(cpu.N)
