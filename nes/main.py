from cpu import CPU

cpu = CPU()

# CLC
# LDA #$03
# SBC #$05
cpu.memory[0x8000] = 0x18
cpu.memory[0x8001] = 0xA9
cpu.memory[0x8002] = 0x03
cpu.memory[0x8003] = 0xE9
cpu.memory[0x8004] = 0x05

cpu.PC = 0x8000

for _ in range(3):
    cpu.step()

print("A =", hex(cpu.A))
print("P =", bin(cpu.P))
