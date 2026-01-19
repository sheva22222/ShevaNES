from cpu import CPU

cpu = CPU()
cpu.A = 0b10000001

cpu.memory[0x8000] = 0x0A  # ASL A
cpu.memory[0x8001] = 0x00  # BRK
cpu.PC = 0x8000

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print("A =", bin(cpu.A))
print("C =", cpu.P & 1)
print("Z =", (cpu.P >> 1) & 1)
print("N =", (cpu.P >> 7) & 1)

