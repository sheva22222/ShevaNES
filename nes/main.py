from cpu import CPU

cpu = CPU()
cpu.A = 0b10000000
cpu.P |= 1  # C = 1

cpu.memory[0x8000] = 0x2A
cpu.memory[0x8001] = 0x00
cpu.PC = 0x8000

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print("A =", bin(cpu.A))
print("C =", cpu.P & 1)
