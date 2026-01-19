from cpu import CPU

cpu = CPU()

cpu.A = 0b00001111

cpu.memory[0x8000] = 0x29  # AND #imm
cpu.memory[0x8001] = 0b11110000
cpu.memory[0x8002] = 0x00  # BRK

cpu.PC = 0x8000

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print("A =", bin(cpu.A))
print("Z =", (cpu.P >> 1) & 1)
print("N =", (cpu.P >> 7) & 1)
