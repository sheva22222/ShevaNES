module ROM

type CartridgeHeader = {
    mapper: int
    prgBanks: int
    chrBanks: int
    mirroring: bool
}

type Cartridge = {
    header: CartridgeHeader
    prg: byte array
    chr: byte array
}

let loadROM (path: string) : Cartridge option =
    try
        let data = System.IO.File.ReadAllBytes(path)
        if data.Length < 16 then None
        else
            let magic = System.Text.Encoding.ASCII.GetString(data, 0, 3)
            if magic <> "NES" then None
            else
                let prgBanks = int data.[4]
                let chrBanks = int data.[5]
                let flags6 = int data.[6]
                let flags7 = int data.[7]
                let mapper = ((flags7 &&& 0xF0) <<< 4) ||| ((flags6 &&& 0xF0) >>> 4)
                let mirroring = (flags6 &&& 0x01) = 1
                
                let prgStart = 16
                let prgSize = prgBanks * 0x4000
                let chrStart = prgStart + prgSize
                let chrSize = chrBanks * 0x2000
                
                let prg = Array.sub data prgStart (min prgSize (data.Length - prgStart))
                let chr = if chrStart < data.Length then
                            Array.sub data chrStart (min chrSize (data.Length - chrStart))
                          else
                            Array.zeroCreate chrSize
                
                Some {
                    header = { mapper = mapper; prgBanks = prgBanks; chrBanks = chrBanks; mirroring = mirroring }
                    prg = prg
                    chr = chr
                }
    with _ -> None