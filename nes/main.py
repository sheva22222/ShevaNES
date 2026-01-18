from cpu import CPU

cpu = CPU()

cpu.PC = 0x8000
cpu.SP = 0xFD
cpu.P  = 0b00100000

# IRQ vector -> 0x9000
cpu.memory[0xFFFE] = 0x00
cpu.memory[0xFFFF] = 0x90

# IRQ handler: RTI
cpu.memory[0x9000] = 0x40  # RTI

print("PC before IRQ =", hex(cpu.PC))
print("SP before IRQ =", hex(cpu.SP))

cpu.irq()

print("PC after IRQ =", hex(cpu.PC))
print("SP after IRQ =", hex(cpu.SP))

cpu.step()  # executes RTI

print("PC after RTI =", hex(cpu.PC))
print("SP after RTI =", hex(cpu.SP))
print("I =", (cpu.P >> 2) & 1)
