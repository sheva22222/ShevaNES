from cpu import CPU

def run(program):
    cpu = CPU()
    cpu.load_program(program)

    # reset vector → 0x8000
    cpu.memory[0xFFFC] = 0x00
    cpu.memory[0xFFFD] = 0x80
    cpu.reset()

    try:
        while True:
            cpu.step()
    except StopIteration:
        pass

    return cpu


cpu = run([
    0x18,  # CLC
    0x00   # BRK
])

print("C =", cpu.P & 1)
print("P =", bin(cpu.P))
print("PC =", hex(cpu.PC))
