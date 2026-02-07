import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollBar
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import colors from styles
try:
    from .styles import CHANNEL_COLORS, COLORS
except ImportError:
    # Fallback colors if styles not available
    CHANNEL_COLORS = [
        '#ff5252', '#ffb142', '#2ccce4', '#33d9b2',
        '#706fd3', '#f78fb3', '#82ccdd', '#b33939'
    ]
    COLORS = {'bg_dark': '#181818', 'bg_tertiary': '#2d2d2d', 'text_primary': '#d4d4d4'}

# Enable OpenGL for hardware acceleration
pg.setConfigOptions(useOpenGL=True, enableExperimental=True, antialias=True)

class WaveformView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.num_channels = 8
        self.channel_colors = CHANNEL_COLORS
        
        # Pin mapping reference (CH -> STM32 Pin)
        self.pin_mapping = {
            0: 'PA0', 1: 'PA1', 2: 'PA2', 3: 'PA3',
            4: 'PA4', 5: 'PA5', 6: 'PA6', 7: 'PA7'
        }
        self.zoom_level = 1.0
        self.updating_scrollbar = False
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Control bar
        controls = QHBoxLayout()
        controls.setContentsMargins(8, 8, 8, 8)
        controls.setSpacing(8)
        
        # Zoom controls
        zoom_label = QLabel("ZOOM")
        zoom_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: bold; font-size: 9pt;")
        controls.addWidget(zoom_label)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setMaximumWidth(40)
        zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_in_btn.setToolTip("Zoom in")
        controls.addWidget(zoom_in_btn)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setMaximumWidth(40)
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_out_btn.setToolTip("Zoom out")
        controls.addWidget(zoom_out_btn)
        
        zoom_fit_btn = QPushButton("Fit")
        zoom_fit_btn.setMaximumWidth(60)
        zoom_fit_btn.clicked.connect(self.zoom_fit)
        zoom_fit_btn.setToolTip("Fit to window")
        controls.addWidget(zoom_fit_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Create plot widget with dark theme
        self.plot_widget = pg.PlotWidget()
        
        # Dark background
        self.plot_widget.setBackground(COLORS['bg_dark'])
        
        # Configure axes
        self.plot_widget.setLabel('bottom', 'Time', units='s', 
                                  color=COLORS['text_primary'])
        self.plot_widget.setLabel('left', 'Channel', 
                                  color=COLORS['text_primary'])
        
        # Style the axes
        axis_pen = pg.mkPen(color=COLORS['text_disabled'], width=1)
        self.plot_widget.getAxis('bottom').setPen(axis_pen)
        self.plot_widget.getAxis('left').setPen(axis_pen)
        self.plot_widget.getAxis('bottom').setTextPen(COLORS['text_secondary'])
        self.plot_widget.getAxis('left').setTextPen(COLORS['text_secondary'])
        
        # Grid styling - subtle and non-intrusive
        self.plot_widget.showGrid(x=True, y=False, alpha=0.1)
        
        # Enable mouse interaction (Horizontal only)
        self.plot_widget.setMouseEnabled(x=True, y=False)
        self.plot_widget.plotItem.setMenuEnabled(False) # Optional: Disable context menu to prevent accidental reset
        
        # Auto-scroll flag
        self.auto_scroll = True
        
        # Connect signals
        self.plot_widget.scene().sigMouseClicked.connect(self.on_mouse_clicked)
        # Connect X range changed to update scrollbar
        self.plot_widget.sigXRangeChanged.connect(self.update_scrollbar_from_plot)
        
        layout.addWidget(self.plot_widget)
        
        # Horizontal Scrollbar
        self.scrollbar = QScrollBar(Qt.Horizontal)
        self.scrollbar.setRange(0, 10000)
        self.scrollbar.valueChanged.connect(self.on_scrollbar_scroll)
        # Style scrollbar to match dark theme
        self.scrollbar.setStyleSheet(f"""
            QScrollBar:horizontal {{
                border: none;
                background: {COLORS['bg_tertiary']};
                height: 14px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: #555;
                min-width: 20px;
                border-radius: 7px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
            }}
        """)
        layout.addWidget(self.scrollbar)
        
        self.setLayout(layout)
        
        # Store plot items
        self.channel_plots = []
        self.channel_labels = []
        self.current_capture = None
    
    def on_mouse_clicked(self, event):
        """Stop auto-scroll on user interaction"""
        if not self.auto_scroll:
             return
        self.auto_scroll = False
        
    def set_auto_scroll(self, enabled):
        """Enable/disable auto-scrolling"""
        self.auto_scroll = enabled
    
    def update_scrollbar_from_plot(self):
        """Update scrollbar position and page size based on plot ViewBox"""
        if self.updating_scrollbar or not self.current_capture:
            return
            
        view_box = self.plot_widget.getViewBox()
        view_range = view_box.viewRange()[0] # [min, max]
        start_time, end_time = view_range
        
        total_time = self.current_capture.time[-1] if len(self.current_capture.time) > 0 else 1.0
        if total_time <= 0: total_time = 1e-9 # Avoid div/0
        
        # Map time to 0-10000 scrollbar range
        # Scrollbar range represents total_time
        # PageStep represents view width
        
        view_width = end_time - start_time
        
        SCROLL_MAX = 10000
        
        # Calculate proportional page step
        page_step = int((view_width / total_time) * SCROLL_MAX)
        page_step = max(10, min(SCROLL_MAX, page_step)) # Clamp
        
        # Calculate position
        # Start time -> value
        value = int((start_time / total_time) * SCROLL_MAX)
        value = max(0, min(SCROLL_MAX - page_step, value))
        
        # Block signals to prevent feedback loop
        self.scrollbar.blockSignals(True)
        self.scrollbar.setPageStep(page_step)
        self.scrollbar.setValue(value)
        self.scrollbar.blockSignals(False)
        
    def on_scrollbar_scroll(self, value):
        """Update plot X range based on scrollbar value"""
        if not self.current_capture:
            return
            
        self.updating_scrollbar = True
        self.auto_scroll = False # User interaction stops auto-scroll
        
        total_time = self.current_capture.time[-1] if len(self.current_capture.time) > 0 else 1.0
        SCROLL_MAX = 10000
        
        view_box = self.plot_widget.getViewBox()
        current_view_width = view_box.viewRange()[0][1] - view_box.viewRange()[0][0]
        
        # Map value to time start
        # value / SCROLL_MAX = start_time / total_time
        # But wait, scrollbar value is typically start of the separate "page".
        
        start_time = (value / SCROLL_MAX) * total_time
        end_time = start_time + current_view_width
        
        self.plot_widget.setXRange(start_time, end_time, padding=0)
        
        self.updating_scrollbar = False

    def zoom_in(self):
        """Zoom in on the waveform"""
        self.auto_scroll = False
        view_box = self.plot_widget.getViewBox()
        view_box.scaleBy((0.5, 1))
    
    def zoom_out(self):
        """Zoom out on the waveform"""
        view_box = self.plot_widget.getViewBox()
        view_box.scaleBy((2, 1))
    
    def zoom_fit(self):
        """Fit waveform to window"""
        self.plot_widget.autoRange()
    
    def display_capture(self, capture, is_rolling_update=False):
        """Display a Capture object with enhanced styling and performance"""
        if not capture or len(capture.time) == 0:
            return
        
        self.current_capture = capture
        
        # Initialize or Clear if not rolling update
        if not is_rolling_update:
             self.plot_widget.clear()
             self.channel_plots = []
             self.channel_labels = []
             self.plot_widget.plotItem.enableAutoRange(pg.ViewBox.XYAxes)
        
        
        # Calculate vertical spacing
        channel_height = 0.8
        channel_spacing = 1.0
        
        # Handle Auto-scrolling calc *before* updating data
        # We want to see a fixed window of time (e.g. 5-10s) or keep user's zoom level
        view_width = 1.0 
        should_scroll = self.auto_scroll and is_rolling_update
        
        if should_scroll:
            vb = self.plot_widget.getViewBox()
            view_range = vb.viewRange()[0]
            view_width = view_range[1] - view_range[0]
            
            # Disable auto-range to prevent jumping
            self.plot_widget.plotItem.disableAutoRange(pg.ViewBox.XAxis)

        # Performance optimization:
        # Instead of downsampling blindly, let's use the full data but
        # rely on OpenGL line drawing which is fast.
        
        max_points = 50000 
        downsample = max(1, len(capture.time) // max_points)
        
        # Determine time window for downsampling?
        # Actually, we can just use all data for now with downsampling logic
        current_time = capture.time[-1]
        
        for ch in range(self.num_channels):
            channel_data = capture.get_channel(ch)
            
            # Efficient indexing for downsampling
            if downsample > 1:
                time_ds = capture.time[::downsample]
                data_ds = channel_data[::downsample]
            else:
                time_ds = capture.time
                data_ds = channel_data
            
            # Create step-like digital waveform
            time_expanded, data_expanded = self._expand_digital(time_ds, data_ds)
            
            # Offset vertically
            y_base = (self.num_channels - 1 - ch) * channel_spacing
            
            # Scale data (0..1)
            data_plot = (data_expanded * channel_height) + y_base
            
            if is_rolling_update and ch < len(self.channel_plots):
                 # Update existing plot
                self.channel_plots[ch].setData(time_expanded, data_plot)
                
                # Update text pos to stay visible? 
                # For now, let's just keep them at start.
            else:
                # Create new plot
                pen = pg.mkPen(color=self.channel_colors[ch], width=1.5)
                
                plot = self.plot_widget.plot(
                    time_expanded, 
                    data_plot,
                    pen=pen,
                    name=f'CH{ch}',
                    antialias=False, 
                    autoDownsample=False 
                )
                if ch >= len(self.channel_plots):
                    self.channel_plots.append(plot)
                else:
                    self.channel_plots[ch] = plot
                
                # Add channel label if new
                if ch >= len(self.channel_labels):
                    pin_name = self.pin_mapping.get(ch, '?')
                    label_text = f'''
                    <div style="font-family: monospace; font-weight: bold;">
                        <span style="color: {self.channel_colors[ch]};">CH{ch}</span>
                        <span style="color: {COLORS['text_secondary']}; font-size: 8pt;">({pin_name})</span>
                    </div>
                    '''
                    text_item = pg.TextItem(html=label_text, anchor=(0, 0.5))
                    text_item.setPos(capture.time[0], y_base + channel_height/2)
                    self.plot_widget.addItem(text_item)
                    self.channel_labels.append(text_item)
                else:
                    # Just update pos
                    self.channel_labels[ch].setPos(capture.time[0], y_base + channel_height/2)

        
        # Set Y axis range
        if not is_rolling_update:
            self.plot_widget.setYRange(-0.5, self.num_channels * channel_spacing + 0.5)
            y_ticks = [((self.num_channels - 1 - i) * channel_spacing + channel_height/2, f'CH{i}') 
                       for i in range(self.num_channels)]
            self.plot_widget.getAxis('left').setTicks([y_ticks])
            self.plot_widget.autoRange()

        # Apply scrolling
        if should_scroll:
            # Shift view to keep latest time on right
            # view_width is from BEFORE the data update
            self.plot_widget.setXRange(current_time - view_width, current_time, padding=0)
    
        self.update_scrollbar_from_plot()

    def _expand_digital(self, time, data):
        """Convert to step waveform by duplicating points using numpy"""
        if len(time) < 2:
            return time, data
        
        # Vectorized step expansion:
        # We repeat time twice, shift one copy, to get start/end of each segment
        # X: [t0, t1, t1, t2, t2, t3...]
        # Y: [d0, d0, d1, d1, d2, d2...]
        
        # Use simple repeat which is very fast
        time_expanded = np.repeat(time, 2)[1:]
        data_expanded = np.repeat(data, 2)[:-1]
        
        return time_expanded, data_expanded
