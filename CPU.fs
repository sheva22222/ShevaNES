module CPU

type CPUState = {
    mutable PC: uint16
    mutable SP: byte
    mutable A: byte
    mutable X: byte
    mutable Y: byte
    mutable P: byte
    mutable cycles: int64
    mutable memory: byte array
}

let create() = {
    PC = 0x8000us
    SP = 0xFDuy
    A = 0uy
    X = 0uy
    Y = 0uy
    P = 0x24uy
    cycles = 0L
    memory = Array.zeroCreate 0x10000
}

let readByte (state: CPUState) (addr: uint16) : byte =
    state.memory.[int addr]

let writeByte (state: CPUState) (addr: uint16) (value: byte) =
    state.memory.[int addr] <- value

let execute (state: CPUState) (opcode: byte) =
    match opcode with
    | 0xEAuy -> () // NOP
    | 0xA9uy -> // LDA immediate
        let value = readByte state (state.PC + 1us)
        state.A <- value
        state.PC <- state.PC + 2us
    | 0xA5uy -> // LDA zero page
        let addr = uint16 (readByte state (state.PC + 1us))
        state.A <- readByte state addr
        state.PC <- state.PC + 2us
    | 0x85uy -> // STA zero page
        let addr = uint16 (readByte state (state.PC + 1us))
        writeByte state addr state.A
        state.PC <- state.PC + 2us
    | _ -> state.PC <- state.PC + 1us
    
    state.cycles <- state.cycles + 1L
