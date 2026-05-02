module Main

open Raylib_cs
open System

[<EntryPoint>]
let main argv =
    let romPath = if argv.Length > 0 then argv.[0] else "super_mario_bros.nes"
    
    match ROM.loadROM romPath with
    | None -> 
        printfn "Error: Could not load ROM from %s" romPath
        1
    | Some rom ->
        let screenWidth = 256
        let screenHeight = 240
        let scale = 3
        
        Raylib.InitWindow(screenWidth * scale, screenHeight * scale, "ShevaNES Emulator")
        Raylib.SetTargetFPS(60)
        
        let cpuState = CPU.createCPU_State ()
        let ppuState = PPU.createPPU ()
        
        ROM.loadPRGToMemory rom cpuState.memory
        ROM.loadCHRToVRAM rom ppuState.vram
        
        let pixels = Array.zeroCreate (screenWidth * screenHeight)
        let texture = Raylib.LoadTextureFromImage(Raylib.GenImageColor(screenWidth, screenHeight, Raylib.Color.Black))
        
        while not (Raylib.WindowShouldClose()) do
            for _ in 1..1789 do
                let opcode = CPU.readMemory cpuState cpuState.cpu.PC
                CPU.execute cpuState opcode
            
            Raylib.BeginDrawing()
            Raylib.ClearBackground(Raylib.Color.Black)
            
            let rec drawRect x y color =
                if x < screenWidth && y < screenHeight then
                    pixels.[y * screenWidth + x] <- color
            
            Raylib.DrawRectangle(10, 10, 100, 100, Raylib.Color.Red)
            
            Raylib.EndDrawing()
        
        Raylib.UnloadTexture(texture)
        Raylib.CloseWindow()
        0