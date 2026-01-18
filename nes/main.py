from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x01,
    0x00
]

irq_handler = [
    0xA9, 0x42,
    0x00
]

cpu.load_program(program, 0x8000)
cpu.load_program(irq_handler, 0x9000)

cpu.memory[0xFFFC] = 0x00
cpu.memory[0xFFFD] = 0x80

cpu.memory[0xFFFE] = 0x00
cpu.memory[0xFFFF] = 0x90

cpu.reset()

cpu.step()
cpu.irq()

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))
