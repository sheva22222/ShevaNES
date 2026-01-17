from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x01,  # LDA #$01
    0xA9, 0x05,  # LDA #$05
]

cpu.load_program(program)

for _ in range(2):
    cpu.step()

print(cpu.A)  # должно быть 5
