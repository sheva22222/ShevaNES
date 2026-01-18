from cpu import CPU

cpu = CPU()

# NMI vector -> 0x9000
cpu.memory[0xFFFA] = 0x00
cpu.memory[0xFFFB] = 0x90

cpu.PC = 0x8000
cpu.SP = 0xFD
cpu.P = 0b00100000  # I = 0

print("PC before NMI =", hex(cpu.PC))
print("SP before NMI =", hex(cpu.SP))

cpu.nmi()

print("PC after NMI =", hex(cpu.PC))
print("SP after NMI =", hex(cpu.SP))
print("I =", (cpu.P >> 2) & 1)

p = cpu.memory[0x0100 + cpu.SP + 1]
low = cpu.memory[0x0100 + cpu.SP + 2]
high = cpu.memory[0x0100 + cpu.SP + 3]

print("Stack P =", bin(p))
print("Stack PC =", hex((high << 8) | low))
