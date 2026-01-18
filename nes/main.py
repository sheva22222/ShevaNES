from cpu import CPU

def run(program):
    cpu = CPU()
    cpu.load_program(program)

    # reset vector
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
    0x78,  # SEI
    0x00   # BRK
])

print("I =", (cpu.P >> 2) & 1)
print("P =", bin(cpu.P))
print("PC =", hex(cpu.PC))
