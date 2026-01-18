from cpu import CPU

cpu = CPU()

# SEC
# LDA #$05
# SBC #$03
# BRK
cpu.memory[0x8000] = 0x38
cpu.memory[0x8001] = 0xA9
cpu.memory[0x8002] = 0x05
cpu.memory[0x8003] = 0xE9
cpu.memory[0x8004] = 0x03
cpu.memory[0x8005] = 0x00

cpu.PC = 0x8000

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print("A =", hex(cpu.A))
print("C =", cpu.P & 1)
print("Z =", (cpu.P >> 1) & 1)
print("N =", (cpu.P >> 7) & 1)
print("V =", (cpu.P >> 6) & 1)
