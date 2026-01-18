cpu = CPU()

# main program
program = [
    0xA9, 0x01,  # LDA #$01
    0xEA,        # NOP (если нет — временно убери)
    0x00         # BRK
]

# irq handler
irq_handler = [
    0xA9, 0x42,  # LDA #$42
    0x00
]

cpu.load_program(program, 0x8000)
cpu.load_program(irq_handler, 0x9000)

# reset vector
cpu.memory[0xFFFC] = 0x00
cpu.memory[0xFFFD] = 0x80

# irq vector
cpu.memory[0xFFFE] = 0x00
cpu.memory[0xFFFF] = 0x90

cpu.reset()

# шаг 1
cpu.step()

# ВЫЗЫВАЕМ IRQ ВРУЧНУЮ
cpu.irq()

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))  # ДОЛЖНО БЫТЬ 0x42
