from cpu import CPU

cpu = CPU()

cpu.A = 0b00000001
cpu.memory[0x0010] = 0b11000000  # N=1, V=1, A&M = 0

cpu.memory[0x8000] = 0x24  # BIT zeropage
cpu.memory[0x8001] = 0x10
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
print("V =", (cpu.P >> 6) & 1)
