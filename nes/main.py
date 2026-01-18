from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x42,  # LDA #$42
    0x00         # BRK
]

cpu.load_program(program, 0x8000)

# reset vector → $8000
cpu.memory[0xFFFC] = 0x00
cpu.memory[0xFFFD] = 0x80

cpu.reset()

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))   # должно быть 0x42
print("PC =", hex(cpu.PC))
