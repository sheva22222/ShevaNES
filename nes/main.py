from cpu import CPU

cpu = CPU()

program = [
    0xA9, 5,      # LDA #5
    0xC9, 5,      # CMP #5
    0xD0, 0x02,   # BNE skip
    0xA9, 1,      # LDA #1
    0x00
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
