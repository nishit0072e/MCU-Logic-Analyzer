# Working Folder - File Structure

## ✅ Created: `g:\logic_analyzer\working\`

This folder contains ONLY the essential files needed to run the STM32 Logic Analyzer application.

## File Structure

```
working/
├── main.py                      # Application entry point
├── device.py                    # STM32 communication protocol
├── capture.py                   # Capture data structure
├── requirements.txt             # Python dependencies
├── README.md                    # Usage instructions
├── firmware_custom_pins.ino     # STM32 firmware
└── gui/                         # GUI components
    ├── main_window.py           # Main application window
    ├── waveform_view.py         # Waveform display
    ├── protocol_panel.py        # Protocol configuration
    ├── protocol_decoders.py     # UART/SPI/I2C decoders
    ├── decoded_data_view.py     # Decoded data table
    └── styles.py                # UI styling
```

## Total Files: 13 files

### Core Application (3 files):
- `main.py` - Entry point
- `device.py` - Device communication
- `capture.py` - Data structure

### GUI Components (6 files):
- `main_window.py` - Main window
- `waveform_view.py` - Waveform display
- `protocol_panel.py` - Protocol settings
- `protocol_decoders.py` - Decoders
- `decoded_data_view.py` - Data table
- `styles.py` - Styling

### Documentation (2 files):
- `README.md` - Instructions
- `requirements.txt` - Dependencies

### Firmware (1 file):
- `LA8_DMA.ino` - STM32 code

## Quick Start

### 1. Install Dependencies
```bash
cd g:\logic_analyzer\working
pip install -r requirements.txt
```

### 2. Run Application
```bash
python main.py
```

## What's NOT Included

The following test/development files are NOT in the working folder:
- `test_*.py` - Test scripts
- `update_*.py` - Update scripts
- `fix_*.py` - Fix scripts
- `build_exe.py` - Build script
- `*.spec` - PyInstaller specs
- Old firmware versions

## Distribution

This `working` folder is ready for:

1. **Direct use**: Run `python main.py`
2. **Building executable**: Use PyInstaller
3. **Sharing**: Zip and share with others
4. **Version control**: Commit to Git

## Building Executable from Working Folder

```bash
cd working
pip install pyinstaller
pyinstaller --name="STM32_Logic_Analyzer" --onefile --windowed main.py
```

Output: `dist/STM32_Logic_Analyzer.exe`

## Summary

✅ Clean, organized folder structure
✅ Only essential files included
✅ Ready to run
✅ Ready to build executable
✅ Ready to distribute

