from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QComboBox, 
                             QLabel, QStatusBar, QFrame, QSplitter, QSlider)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont
from .waveform_view import WaveformView
from .styles import get_main_stylesheet, get_status_indicator_html, COLORS
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from device import LogicAnalyzerDevice
from capture import Capture

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.device = None
        self.current_capture = None
        self.live_mode = False
        self.capture_count = 0
        
        # Live capture timer
        self.live_timer = QTimer()
        self.live_timer.timeout.connect(self.do_capture)
        self.live_interval_ms = 500  # Default 500ms
        
        # Professional Title
        self.setWindowTitle("STM32 Logic Analyzer Pro")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply modern stylesheet
        self.setStyleSheet(get_main_stylesheet())
        
        self.setup_ui()
    
    def setup_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar container with background
        toolbar_container = QWidget()
        toolbar_container.setObjectName("toolbar")
        toolbar_layout = QVBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(16, 12, 16, 12)
        toolbar_layout.setSpacing(12)
        
        # ROW 1: Connection and Capture Controls
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        
        # Connection Section
        conn_label = QLabel("CONNECTION")
        conn_label.setObjectName("sectionLabel")
        row1.addWidget(conn_label)
        
        row1.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(120)
        self.port_combo.setToolTip("Select serial port")
        self.refresh_ports()
        row1.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setToolTip("Refresh ports")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        row1.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setObjectName("connectBtn")
        self.connect_btn.setToolTip("Connect to device")
        self.connect_btn.setMinimumWidth(100)
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setProperty("connected", False)
        row1.addWidget(self.connect_btn)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setFrameShadow(QFrame.Sunken)
        row1.addWidget(sep1)
        
        # Capture Section
        cap_label = QLabel("CAPTURE")
        cap_label.setObjectName("sectionLabel")
        row1.addWidget(cap_label)
        
        row1.addWidget(QLabel("Sample Rate:"))
        self.rate_combo = QComboBox()
        self.rate_combo.setMinimumWidth(160)
        self.rate_combo.addItems([
            "100 Hz (20s window)",
            "1 kHz (2s window)",
            "10 kHz (200ms window)",
            "100 kHz (20ms window)",
            "1 MHz (2ms window)",
            "2 MHz (1ms window)",
            "5 MHz (0.4ms window)",
            "6 MHz (0.3ms window)",
        ])
        self.rate_combo.setCurrentIndex(4)
        self.rate_combo.setToolTip("Sample rate (time window for 2048 samples)")
        self.rate_combo.currentIndexChanged.connect(self.on_rate_changed)
        row1.addWidget(self.rate_combo)
        
        self.capture_btn = QPushButton("Capture")
        self.capture_btn.setObjectName("captureBtn")
        self.capture_btn.setToolTip("Start single capture")
        self.capture_btn.clicked.connect(self.do_capture)
        self.capture_btn.setEnabled(False)
        row1.addWidget(self.capture_btn)
        
        row1.addStretch()
        
        # Sample rate display
        self.sample_rate_label = QLabel("Rate: --")
        self.sample_rate_label.setStyleSheet(f"color: {COLORS['accent_secondary']}; font-weight: bold;")
        row1.addWidget(self.sample_rate_label)
        
        toolbar_layout.addLayout(row1)
        
        # ROW 2: Live Capture Controls
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        
        # Live mode section
        live_label = QLabel("LIVE MODE")
        live_label.setObjectName("sectionLabel")
        row2.addWidget(live_label)
        
        self.live_btn = QPushButton("Start Live")
        self.live_btn.setCheckable(True)
        self.live_btn.setToolTip("Toggle live capture mode")
        self.live_btn.setMinimumWidth(100)
        self.live_btn.clicked.connect(self.toggle_live_mode)
        self.live_btn.setEnabled(False)
        row2.addWidget(self.live_btn)
        
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.setToolTip("Pause/Resume live update")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        row2.addWidget(self.pause_btn)
        
        row2.addWidget(QLabel("Interval:"))
        
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(100)
        self.interval_slider.setMaximum(5000)
        self.interval_slider.setValue(500)
        self.interval_slider.setMaximumWidth(200)
        self.interval_slider.setToolTip("Live capture interval (100ms - 5s)")
        self.interval_slider.valueChanged.connect(self.update_live_interval)
        row2.addWidget(self.interval_slider)
        
        self.interval_label = QLabel("500ms")
        self.interval_label.setStyleSheet(f"color: {COLORS['accent_secondary']}; font-weight: bold;")
        self.interval_label.setMinimumWidth(60)
        row2.addWidget(self.interval_label)
        
        row2.addStretch()
        
        toolbar_layout.addLayout(row2)
        
        layout.addWidget(toolbar_container)
        
        # Status Indicator below toolbar
        self.status_indicator = QLabel()
        self.status_indicator.setTextFormat(Qt.RichText)
        self.status_indicator.setContentsMargins(16, 8, 16, 8)
        self.update_status_indicator("disconnected", "Disconnected")
        layout.addWidget(self.status_indicator)
        
        # Main content area - Waveform View only
        # No splitter needed anymore as we removed the protocol panel
        self.waveform_view = WaveformView()
        layout.addWidget(self.waveform_view, 1) # 1 stretch factor to take remaining space
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def update_status_indicator(self, status, text):
        """Update the status indicator with colored dot"""
        html = get_status_indicator_html(status, text)
        self.status_indicator.setText(html)
    
    def refresh_ports(self):
        self.port_combo.clear()
        ports = LogicAnalyzerDevice.list_ports()
        if ports:
            self.port_combo.addItems(ports)
        else:
            self.port_combo.addItem("No ports found")
    
    def toggle_connection(self):
        if self.device and self.device.serial:
            # Disconnect
            self.device.disconnect()
            self.device = None
            self.connect_btn.setText("Connect")
            self.connect_btn.setProperty("connected", False)
            self.connect_btn.setStyle(self.connect_btn.style())  # Refresh style
            self.capture_btn.setEnabled(False)
            self.update_status_indicator("disconnected", "Disconnected")
            self.status_bar.showMessage("Disconnected from device")
            self.sample_rate_label.setText("Rate: --")
            self.live_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
        else:
            # Connect
            port = self.port_combo.currentText()
            if port == "No ports found":
                self.status_bar.showMessage("No serial ports available")
                return
            
            try:
                self.device = LogicAnalyzerDevice(port)
                if self.device.connect():
                    self.connect_btn.setText("Disconnect")
                    self.connect_btn.setProperty("connected", True)
                    self.connect_btn.setStyle(self.connect_btn.style())  # Refresh style
                    self.capture_btn.setEnabled(True)
                    self.live_btn.setEnabled(True)
                    info = self.device.device_info
                    self.update_status_indicator("connected", "Connected")
                    self.status_bar.showMessage(
                        f"Connected to {info['device_name']} v{info['version']} on {port}"
                    )
                else:
                    self.update_status_indicator("error", "Connection Failed")
                    self.status_bar.showMessage(f"Failed to connect to {port}")
                    self.device = None
            except PermissionError:
                self.update_status_indicator("error", "Port In Use")
                self.status_bar.showMessage(
                    f"{port} is in use by another program. Close other applications and try again."
                )
                self.device = None
            except Exception as e:
                self.update_status_indicator("error", "Connection Error")
                error_msg = str(e)
                if "PermissionError" in error_msg or "Access is denied" in error_msg:
                    self.status_bar.showMessage(
                        f"{port} is in use. Close other serial programs."
                    )
                elif "FileNotFoundError" in error_msg or "could not open port" in error_msg:
                    self.status_bar.showMessage(f"{port} not found. Check device connection.")
                else:
                    self.status_bar.showMessage(f"Error: {error_msg}")
                self.device = None
    
    def do_capture(self):
        if not self.device:
            return
        
        # Don't disable button in live mode
        if not self.live_mode:
            self.update_status_indicator("capturing", "Capturing...")
            self.status_bar.showMessage("Capturing data...")
            self.capture_btn.setEnabled(False)
        
        # Capture (blocking for now)
        frame = self.device.capture()
        
        if frame and frame['type'] == 'capture':
            new_capture = Capture(
                frame['samples'],
                frame['sample_period_ns']
            )
            
            if self.live_mode and self.current_capture:
                # Append to existing capture
                self.current_capture.append_samples(frame['samples'])
                
            if self.live_mode:
                # Live Buffer Management
                if self.full_capture is None:
                    # First frame of live capture
                    self.full_capture = new_capture
                    self.current_capture = self.full_capture
                else:
                    # Append to existing buffer
                    self.full_capture.append_samples(frame['samples'])
                    # Enforce 5-minute rolling buffer (300 seconds)
                    self.full_capture.keep_duration(300.0)
                    self.current_capture = self.full_capture

                # Update display
                self.waveform_view.display_capture(self.current_capture, is_rolling_update=True)
                
                rate = new_capture.get_sample_rate_mhz()
                self.sample_rate_label.setText(f"Rate: {rate:.2f} MHz")
                self.status_bar.showMessage(
                    f"Live: {self.current_capture.sample_count} samples buffered"
                )
                self.update_status_indicator("capturing", "Live Capture")
            else:
                # New capture (single shot)
                self.current_capture = new_capture
                self.capture_count += 1
                
                # Display
                self.waveform_view.display_capture(new_capture)
                
                rate = new_capture.get_sample_rate_mhz()
                self.sample_rate_label.setText(f"Rate: {rate:.2f} MHz")
                
                self.update_status_indicator("connected", "Connected")
                self.status_bar.showMessage(
                    f"Captured {new_capture.sample_count} samples @ {rate:.2f} MHz"
                )
        else:
            self.update_status_indicator("error", "Capture Failed")
            self.status_bar.showMessage("Capture failed")
            if self.live_mode:
                self.toggle_live_mode()  # Stop live mode on error
        
        if not self.live_mode:
            self.capture_btn.setEnabled(True)
    
    def toggle_live_mode(self):
        """Toggle live capture mode"""
        self.live_mode = self.live_btn.isChecked()
        
        if self.live_mode:
            # Start live capture
            self.capture_count = 0
            self.current_capture = None  # Reset buffer
            self.full_capture = None     # Reset full capture buffer
            self.live_btn.setText("Stop Live")
            # Style update for active state
            self.live_btn.setStyleSheet(f"background-color: {COLORS['error']}; border: 1px solid {COLORS['error']}; color: white;")
            self.capture_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.pause_btn.setChecked(False)
            self.pause_btn.setText("Pause")
            
            self.update_status_indicator("capturing", "Live Capture")
            self.status_bar.showMessage(f"Live capture started (interval: {self.live_interval_ms}ms)")
            
            # Start timer
            self.live_timer.start(self.live_interval_ms)
        else:
            # Stop live capture
            self.live_timer.stop()
            self.live_btn.setText("Start Live")
            self.live_btn.setStyleSheet("")
            self.capture_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.pause_btn.setChecked(False)
            
            self.update_status_indicator("connected", "Connected")
            self.status_bar.showMessage(f"Live capture stopped")

    def toggle_pause(self):
        """Pause/Resume live capture"""
        is_paused = self.pause_btn.isChecked()
        
        if is_paused:
            self.live_timer.stop()
            self.pause_btn.setText("Resume")
            self.update_status_indicator("warning", "Paused")
            self.waveform_view.set_auto_scroll(False) # Stop scrolling
        else:
            self.live_timer.start(self.live_interval_ms)
            self.pause_btn.setText("Pause")
            self.update_status_indicator("capturing", "Live Capture")
            self.waveform_view.set_auto_scroll(True) # Resume scrolling
    
    def update_live_interval(self, value):
        """Update live capture interval"""
        self.live_interval_ms = value
        self.interval_label.setText(f"{value}ms")
        
        # Update timer if running
        if self.live_mode:
            self.live_timer.setInterval(value)
            self.status_bar.showMessage(f"Live interval: {value}ms")

    def on_rate_changed(self, index):
        """Handle sample rate change"""
        if not self.device:
            return
        
        # Map index to firmware command (slowest to fastest)
        rate_commands = {
            0: ('E', "100 Hz"),
            1: ('D', "1 kHz"),
            2: ('B', "10 kHz"),
            3: ('A', "100 kHz"),
            4: ('1', "1 MHz"),
            5: ('2', "2 MHz"),
            6: ('5', "5 MHz"),
            7: ('6', "6 MHz"),
        }
        
        if index in rate_commands:
            cmd, rate_name = rate_commands[index]
            success = self.device.set_sample_rate(cmd)
            if success:
                self.status_bar.showMessage(f"Sample rate set to {rate_name}")
            else:
                self.status_bar.showMessage(f"Failed to set sample rate to {rate_name}")
