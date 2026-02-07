# Build Instructions for Linux

This project uses **PyInstaller** to create standalone executables.

## Prerequisites

1.  **Python 3.8+** installed.
2.  **Virtual Environment** (Recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    pip install pyinstaller
    ```

## Building the Executable

Run the following command in the project root:

```bash
pyinstaller --name="STM32_Logic_Analyzer" --noconsole --onefile main.py
```

-   `--name`: Sets the output filename.
-   `--noconsole`: Hides the terminal window (GUI only).
-   `--onefile`: Bundles everything into a single ELF executable.

## Output

The executable will be located in the `dist/` directory:

```bash
./dist/STM32_Logic_Analyzer
```

## Creating a Desktop Entry

To integrate with your desktop environment (GNOME, KDE, etc.), create a file named `~/.local/share/applications/stm32-logic-analyzer.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=STM32 Logic Analyzer
Comment=8-Channel Logic Analyzer Interface
Exec=/path/to/your/dist/STM32_Logic_Analyzer
Icon=/path/to/your/icon.png
Terminal=false
Categories=Development;Electronics;
```

Make it executable:
```bash
chmod +x ~/.local/share/applications/stm32-logic-analyzer.desktop
```
