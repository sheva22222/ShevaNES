from cpu import CPU

cpu = CPU()

program = [
    0x4C, 0x05, 0x00,  # JMP $0005
    0xA9, 0x01,        # LDA #$01 (пропуск)
    0xA9, 0x05,        # LDA #$05
    0x00
]

cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))
