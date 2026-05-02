# ShevaNES - F# NES Emulator for Android

NES ��мулятор на F#, работающий на Android платформе.

## Возможности
- 6502 CPU эмуляция
- PPU графический процессор
- Загрузка iNES ROM файлов
- Поддержка Android 5.0+
- Автоматическая сборка через GitHub Actions

## Требования
- .NET 8.0 SDK
- Android SDK API 21+
- MAUI workload: `dotnet workload install maui-android`

## Сборка

### Локально
```bash
dotnet build
dotnet publish -f net8.0-android -c Release
```

### GitHub Actions
Каждый push автоматически собирает APK и загружает его в Artifacts.

## Использование
1. Установите APK на Android устройство
2. Откройте приложение
3. Выберите NES ROM файл
4. Нажмите Play

## Структура проекта
- `CPU.fs` - 6502 процессор
- `PPU.fs` - видеопроцессор
- `ROM.fs` - загрузчик ROM
- `MainPage.xaml.fs` - UI интерфейс
- `.github/workflows/android-build.yml` - GitHub Actions конфигурация