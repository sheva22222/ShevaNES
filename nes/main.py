from cpu import CPU

cpu = CPU()

# LDA #$42
program = [
    0xA9, 0x42
]

cpu.load_program(program)
cpu.step()

print(cpu.A)  # должно вывести 66
