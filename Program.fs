open System

[<EntryPoint>]
let main args =
    try
        MauiProgram.CreateMauiApp().CreateWindow().ShowAsync() |> ignore
        0
    with e ->
        printfn "Error: %s" e.Message
        1