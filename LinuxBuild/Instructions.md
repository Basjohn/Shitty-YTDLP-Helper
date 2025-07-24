# Linux Build Instructions for Shitty YT-DLP Helper

## Dependencies

### Required Dependencies
1. Python 3.8 or higher
2. pip (Python package manager)
3. FFmpeg (for video/audio processing)

### Install Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3-pip ffmpeg
```

#### Fedora
```bash
sudo dnf install -y python3-pip ffmpeg
```

#### Arch Linux
```bash
sudo pacman -S --needed python-pip ffmpeg
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Make the script executable:
```bash
chmod +x shitty_ytdlphelper.py
```

3. (Optional) Install the desktop entry for application menu integration:
```bash
mkdir -p ~/.local/share/applications/
cp shitty-ytdlp-helper.desktop ~/.local/share/applications/
```

## Building (Optional)

To create a standalone executable:

1. Install PyInstaller if you haven't already:
```bash
pip install pyinstaller
```

2. Run the build script:
```bash
python build_simple.py
```

The built application will be in the `dist` directory.

## Running the Application

### From Source
```bash
python3 shitty_ytdlphelper.py
```

### If Built with PyInstaller
```bash
./dist/shitty_ytdlphelper/shitty_ytdlphelper
```

## Troubleshooting

- If you get a "command not found" error, try using `python3` instead of `python`
- If you encounter any issues with FFmpeg, ensure it's properly installed and in your system PATH
- For Wayland users: If the window doesn't display properly, try running with:
  ```bash
  QT_QPA_PLATFORM=xcb python3 shitty_ytdlphelper.py
  ```
