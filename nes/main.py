from cpu import CPU

cpu = CPU()

program = [
    0xA9, 10,     # LDA #10
    0x69, 5       # ADC #5
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(cpu.A)
print(cpu.C)
