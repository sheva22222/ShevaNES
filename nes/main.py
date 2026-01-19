from cpu import CPU

cpu = CPU()

with open("nestest.nes", "rb") as f:
    rom = f.read()

prg = rom[16:16+0x4000]

for i in range(0x4000):
    cpu.memory[0x8000 + i] = prg[i]
    cpu.memory[0xC000 + i] = prg[i]

cpu.PC = 0xC000
cpu.SP = 0xFD
cpu.P  = 0x24

while True:
    cpu.step()
