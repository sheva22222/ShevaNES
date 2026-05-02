namespace ShevaNES

open Microsoft.Maui
open Microsoft.Maui.Hosting

module MauiProgram =
    let CreateMauiApp() =
        let builder = MauiApp.CreateBuilder()
        builder
            .UseMauiApp<App>()
            .ConfigureFonts(fun fonts ->
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular") |> ignore
            )
            |> ignore
        builder.Build()