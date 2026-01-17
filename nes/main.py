from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x2A,  # LDA #42
    0x85, 0x10,  # STA $10
]

cpu.load_program(program)

cpu.step()
cpu.step()

print(cpu.memory[0x10])
