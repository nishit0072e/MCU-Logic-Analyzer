# STM32 Logic Analyzer - Working Version

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Application

```bash
python main.py
```

## Files Included

### Essential Application Files:
- `main.py` - Application entry point
- `device.py` - STM32 communication protocol
- `gui/` - GUI components
  - `main_window.py` - Main application window
  - `waveform_view.py` - Waveform display
  - `protocol_panel.py` - Protocol decoder configuration
  - `protocol_decoders.py` - UART/SPI/I2C decoders
  - `decoded_data_view.py` - Decoded data table
  - `styles.py` - UI styling

### Firmware:
- `firmware_custom_pins.ino` - STM32F103C6 firmware

## Hardware Setup

### STM32 Pin Mapping:
- **CH0**: PB12
- **CH1**: PB13
- **CH2**: PB14
- **CH3**: PB15
- **CH4**: PB4
- **CH5**: PB5
- **CH6**: PB6
- **CH7**: PB7
- **UART**: PA9 (TX), PA10 (RX) @ 115200 baud

### Connections:
1. Flash `firmware_custom_pins.ino` to STM32F103C6
2. Connect STM32 UART to PC via USB-Serial adapter
3. Connect signals to input pins (PB12-15, PB4-7)

## Features

- **8 Channels** @ up to 6MHz sample rate
- **2048 Sample Buffer**
- **8 Sample Rates**: 100Hz, 1kHz, 10kHz, 100kHz, 1MHz, 2MHz, 5MHz, 6MHz
- **Live Capture Mode**: Continuous monitoring
- **Protocol Decoders**: UART, SPI, I2C
- **Export**: Save decoded data

## Usage

1. **Connect**: Select COM port and click "● Connect"
2. **Configure**: Choose sample rate (e.g., 1 MHz for UART)
3. **Capture**: Click "▶ Capture" or use "▶ Start Live"
4. **Decode**: Select protocol, configure settings, click "Apply Decoder"
5. **View**: See waveforms and decoded data

## Building Standalone Executable

To create a Windows .exe file:

```bash
pip install pyinstaller
python build_exe.py
```

Output: `dist/STM32_Logic_Analyzer.exe`

## System Requirements

- **OS**: Windows 10/11
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum
- **USB**: USB-Serial adapter (FTDI, CH340, etc.)

## Troubleshooting

### "No module named 'PyQt5'"
```bash
pip install -r requirements.txt
```

### "Could not open port"
- Check COM port in Device Manager
- Close other applications using the port
- Try different USB port

### "Device is BUSY"
- Wait for reset to complete
- Click Capture again
- Press STM32 reset button if needed

## License

MIT License - Free to use and modify

## Support

For issues and questions, check the documentation in the parent folder.
