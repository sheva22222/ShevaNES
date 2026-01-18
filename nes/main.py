from cpu import CPU

cpu = CPU()

# reset vector -> $8000
cpu.memory[0xFFFC] = 0x00
cpu.memory[0xFFFD] = 0x80

# program
cpu.memory[0x8000] = 0xEA  # NOP
cpu.memory[0x8001] = 0xEA  # NOP
cpu.memory[0x8002] = 0x00  # BRK

cpu.reset()

try:
    while True:
        cpu.step()
except StopIteration:
    print("OK, NOP works")
