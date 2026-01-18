from cpu import CPU

cpu = CPU()

# --------------------
# программа
# --------------------
program = [
    0xEA,  # NOP
    0xEA,  # NOP
    0x00   # BRK (на всякий)
]

cpu.load_program(program)

# reset vector → 0x8000
cpu.memory[0xFFFC] = 0x00
cpu.memory[0xFFFD] = 0x80

# IRQ vector → 0x9000
cpu.memory[0xFFFE] = 0x00
cpu.memory[0xFFFF] = 0x90

cpu.reset()

# Разрешаем IRQ
cpu.P &= 0b11111011  # CLI вручную (I = 0)

print("PC before IRQ =", hex(cpu.PC))
print("SP before IRQ =", hex(cpu.SP))

# 🔥 ВЫЗЫВАЕМ IRQ
cpu.irq()

print("PC after IRQ =", hex(cpu.PC))
print("SP after IRQ =", hex(cpu.SP))
print("I =", (cpu.P >> 2) & 1)

# Проверим стек
p = cpu.memory[0x0100 + cpu.SP + 1]
low = cpu.memory[0x0100 + cpu.SP + 2]
high = cpu.memory[0x0100 + cpu.SP + 3]

print("Stack P =", bin(p))
print("Stack PC =", hex((high << 8) | low))
