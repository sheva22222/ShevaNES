from cpu import CPU

cpu = CPU()

# --- мини тест JMP (indirect) ---
cpu.memory[0x3000] = 0x6C      # opcode JMP ($12FF)
cpu.memory[0x3001] = 0xFF
cpu.memory[0x3002] = 0x12

cpu.memory[0x12FF] = 0x34
cpu.memory[0x1200] = 0x56      # 6502 bug

cpu.PC = 0x3000

try:
    cpu.step()
except StopIteration:
    pass

print("PC =", hex(cpu.PC))     # ОЖИДАЕМО: 0x5634
