from cpu import CPU

cpu = CPU()

# main program
program = [
    0xA9, 0x01,  # LDA #$01
    0xEA,        # NOP
    0x00         # BRK
]

# irq handler
irq_handler = [
    0xA9, 0x42,  # LDA #$42
    0x40         # RTI
]

cpu.load_program(program, 0x8000)
cpu.load_program(irq_handler, 0x9000)

cpu.memory[0xFFFC] = 0x00
cpu.memory[0xFFFD] = 0x80

cpu.memory[0xFFFE] = 0x00
cpu.memory[0xFFFF] = 0x90

cpu.reset()

cpu.step()   # LDA #$01
cpu.irq()    # IRQ

cpu.step()   # LDA #$42
cpu.step()   # RTI

cpu.step()   # NOP (возврат!)

print(hex(cpu.A))   # должно быть 0x42
print("PC =", hex(cpu.PC))
