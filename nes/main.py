from cpu import CPU

cpu = CPU()

# программа
cpu.memory[0x8000] = 0x00  # BRK

# вектор BRK/IRQ
cpu.memory[0xFFFE] = 0x00
cpu.memory[0xFFFF] = 0x90  # PC -> 0x9000

cpu.PC = 0x8000

print("PC before =", hex(cpu.PC))
print("SP before =", hex(cpu.SP))

cpu.step()

print("PC after =", hex(cpu.PC))
print("SP after =", hex(cpu.SP))

p = cpu.memory[0x0100 + cpu.SP + 1]
print("Stack P =", bin(p))
