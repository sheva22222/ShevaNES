namespace ShevaNES

open Microsoft.Maui
open Microsoft.Maui.Controls
open System

type MainPage() as this =
    inherit ContentPage()
    
    let mutable romPath = ""
    let mutable cpu = CPU.create()
    let mutable ppu = PPU.create()
    
    do
        let verticalStack = VerticalStackLayout()
        verticalStack.Spacing <- 10.0
        verticalStack.Padding <- Thickness(20.0)
        verticalStack.VerticalOptions <- LayoutOptions.FillAndExpand
        
        let title = Label(
            Text = "ShevaNES - NES Emulator",
            FontSize = 24.0,
            FontAttributes = FontAttributes.Bold,
            HorizontalOptions = LayoutOptions.Center
        )
        verticalStack.Add(title)
        
        let romLabel = Label(
            Text = "No ROM loaded",
            FontSize = 14.0,
            HorizontalOptions = LayoutOptions.Center
        )
        verticalStack.Add(romLabel)
        
        let fileButton = Button(
            Text = "📁 Select NES ROM",
            HorizontalOptions = LayoutOptions.Fill,
            Padding = Thickness(10.0)
        )
        fileButton.Clicked.Add(fun _ -> 
            Application.Current.MainPage.DisplayAlert("Info", "ROM Selection Feature", "OK") |> ignore
        )
        verticalStack.Add(fileButton)
        
        let playButton = Button(
            Text = "▶ Play Game",
            HorizontalOptions = LayoutOptions.Fill,
            Padding = Thickness(10.0),
            IsEnabled = false
        )
        playButton.Clicked.Add(fun _ ->
            Application.Current.MainPage.DisplayAlert("Info", "Starting Emulation", "OK") |> ignore
        )
        verticalStack.Add(playButton)
        
        let statusLabel = Label(
            Text = "Ready",
            FontSize = 12.0,
            HorizontalOptions = LayoutOptions.Center,
            Margin = Thickness(0.0, 20.0, 0.0, 0.0)
        )
        verticalStack.Add(statusLabel)
        
        this.Content <- verticalStack