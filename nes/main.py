from cpu import CPU6502
from bus import Bus

bus = Bus()
cpu = CPU6502(bus)

# Программа:
# LDA #$05
# STA $0002
# JMP $8000
program = [
    0xA9, 0x05,
    0x85, 0x02,
    0x4C, 0x00, 0x80
]

bus.prg[:len(program)] = program

# Reset vector → 0x8000
bus.ram[0xFFFC % 0x0800] = 0x00
bus.ram[0xFFFD % 0x0800] = 0x80

cpu.reset()

for i in range(5):
    cpu.step()
    print(f"Step {i}: A={cpu.A}, RAM[2]={bus.ram[2]}")
  
