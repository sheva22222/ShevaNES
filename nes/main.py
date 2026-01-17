from cpu import CPU

cpu = CPU()

program = [
    0xA9, 0x01,       # LDA #$01 → N = 0
    0x10, 0x02,       # BPL +2 (сработает)
    0xA9, 0xFF,       # LDA #$FF (пропуск)
    0xA9, 0x05        # LDA #$05
]


cpu.load_program(program)

try:
    while True:
        cpu.step()
except StopIteration:
    pass

print(hex(cpu.A))
print("N =", (cpu.P >> 7) & 1)
