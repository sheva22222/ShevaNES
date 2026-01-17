from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x00,
]

cpu.load_program(program)
cpu.step()

print(bin(cpu.P))
