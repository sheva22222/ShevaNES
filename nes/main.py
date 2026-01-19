from cpu import CPU

cpu = CPU()
cpu.memory[0x0010] = 0x01

cpu.memory[0x8000] = 0xC6  # DEC zp
cpu.memory[0x8001] = 0x10
cpu.memory[0x8002] = 0x00  # BRK
cpu.PC = 0x8000

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.memory[0x0010]))  # 0x0
print("Z =", (cpu.P >> 1) & 1)  # 1
print("N =", (cpu.P >> 7) & 1)  # 0
