module PPU

type PPUState = {
    mutable scanline: int
    mutable cycle: int
    mutable vram: byte array
    mutable palette: byte array
}

let create() = {
    scanline = 0
    cycle = 0
    vram = Array.zeroCreate 0x4000
    palette = Array.zeroCreate 32
}

let tick (ppu: PPUState) =
    ppu.cycle <- ppu.cycle + 1
    if ppu.cycle >= 341 then
        ppu.cycle <- 0
        ppu.scanline <- ppu.scanline + 1
        if ppu.scanline >= 261 then
            ppu.scanline <- 0

let renderFrame (ppu: PPUState) : byte array =
    Array.zeroCreate (256 * 240)