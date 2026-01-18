from cpu import CPU

cpu = CPU()

cpu.P = 0b10000000  # N = 1
cpu.SP = 0xFD

cpu.memory[0x8000] = 0x08  # PHP
cpu.memory[0x8001] = 0x00  # BRK
cpu.PC = 0x8000

print("SP before =", hex(cpu.SP))
print("P before  =", bin(cpu.P))

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print("SP after  =", hex(cpu.SP))
print("Stack P  =", bin(cpu.memory[0x0100 + cpu.SP + 1]))
print("P after  =", bin(cpu.P))
