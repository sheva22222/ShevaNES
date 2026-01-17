from cpu import CPU

cpu = CPU()

program = [
    0x20, 0x05, 0x80,  # JSR $8005
    0xA9, 1,          # LDA #1
    0x00,             # BRK
    0xA9, 42,         # sub: LDA #42
    0x60              # RTS
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(cpu.A)
