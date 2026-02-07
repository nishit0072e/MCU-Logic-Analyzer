# STM32 Logic Analyzer (LA8) 🚀

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux-blue)
![Hardware](https://img.shields.io/badge/Hardware-STM32F103-green)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)

**A professional-grade, 8-channel Logic Analyzer for <$5.**

Turn your generic STM32 Blue Pill development board into a powerful digital signal analysis tool. With **6 MHz** theoretical sampling rate, **zero-jitter DMA acquisition**, and a hardware-accelerated **OpenGL** interface, the LA8 bridges the gap between hobbyist toys and expensive benchtop equipment.

---

## ✨ Key Features

*   **⚡ High Performance**: Up to **6 MHz** sample rate (hardware timer driven).
*   **🎯 Zero Jitter**: DMA-based acquisition ensures theoretically perfect timing stability.
*   **🖥️ Fluid UI**: **60 FPS** waveform rendering using hardware-accelerated OpenGL (`pyqtgraph`).
*   **📡 8 Channels**: Parallel capture on pins **PA0 - PA7**.
*   **🔄 Live View**: Continuous "Rolling Buffer" mode with auto-scroll and 5-minute retention history.
*   **🛠️ Professional Tools**:
    *   Horizontal Scrollbar & Zooming.
    *   Pause/Resume analysis.
    *   Dark Mode UI.

---

## 🏗️ Architecture

The system uses a distributed architecture to overcome the bandwidth limitations of standard UART.

1.  **Distributed Processing**:
    *   **Edge (STM32)**: Handles Hard Real-Time signal acquisition into internal SRAM.
    *   **Host (PC)**: Handles Soft Real-Time visualization and massive data buffering.
2.  **Store-and-Forward Protocol**:
    *   The STM32 captures a "burst" of data at high speed (e.g., 6 MB/s).
    *   It buffers this data and transmits it to the PC at UART speeds (11.5 KB/s).
    *   The PC software stitches these bursts together to create a seamless timeline.

👉 **[Read the Engineering Whitepaper](docs/technical_whitepaper.md)** for a deep dive into the DMA engine and design trade-offs.

---

## 🚀 Getting Started

### 1. Hardware Setup
You need an **STM32F103C8T6** ("Blue Pill") or similar board and a USB-to-TTL Serial adapter.

**Wiring**:
*   **Signal Inputs**: `PA0` to `PA7` (Channel 0 - 7).
*   **UART**:
    *   STM32 `PA9` (TX) -> Serial Adapter `RX`.
    *   STM32 `PA10` (RX) -> Serial Adapter `TX`.
*   **Power**: 3.3V or 5V (Common Ground is critical!).

### 2. Flashing Firmware
1.  Open `firmware/stm32_logic_analyzer.ino` in Arduino IDE.
2.  Select board: **Generic STM32F103C series**.
3.  Flash via ST-Link or Serial.

### 3. Running the Software

**Option A: Standalone Executable (Windows)**
*   Download the latest release.
*   Run `STM32_Logic_Analyzer.exe`.

**Option B: Python Source**
```bash
# Install dependencies
pip install -r software/requirements.txt

# Run
python software/main.py
```

**Linux Users**: Check [Build Instructions](docs/build_instructions_linux.md).

---

## 📸 Screenshots

*(Add your screenshots here)*

---

## 🤝 Contributing
Contributions are welcome! Please read the [implementation plan](docs/technical_whitepaper.md) to understand the architectural constraints before optimizing.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
