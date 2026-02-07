"""
Modern professional dark theme stylesheet for Logic Analyzer GUI
"""

# Color Palette - Professional Dark Theme (VS Code / JetBrains inspired)
COLORS = {
    # Backgrounds
    'bg_primary': '#1e1e1e',    # Main window background (VS Code dark)
    'bg_secondary': '#252526',  # Sidebars, panels
    'bg_tertiary': '#2d2d2d',   # Inputs, hover states
    'bg_header': '#333333',     # Headers, toolbars
    'bg_dark': '#181818',       # Plot background, status bar
    
    # Accents
    'accent_primary': '#007acc',    # VS Code Blue
    'accent_secondary': '#0098ff',  # Lighter Blue
    'accent_hover': '#005f9e',      # Darker Blue
    
    # Status
    'success': '#4ec9b0', # Greenish
    'warning': '#cca700', # Amber
    'error': '#f14c4c',   # Red
    'info': '#9cdcfe',    # Light Blue
    
    # Text
    'text_primary': '#d4d4d4',   # Main text
    'text_secondary': '#858585', # Subtitles, comments
    'text_disabled': '#585858',  # Disabled text
    'text_bright': '#ffffff',    # Highlights
    
    # Borders
    'border_light': '#3e3e42',
    'border_dark': '#1e1e1e',
    
    # Channel Colors (High contrast, professional)
    'ch0': '#ff5252',  # Red
    'ch1': '#ffb142',  # Orange
    'ch2': '#2ccce4',  # Cyan
    'ch3': '#33d9b2',  # Teal
    'ch4': '#706fd3',  # Purple
    'ch5': '#f78fb3',  # Pink
    'ch6': '#82ccdd',  # Light Blue
    'ch7': '#b33939',  # Dark Red
}

# Get channel colors as list
CHANNEL_COLORS = [COLORS[f'ch{i}'] for i in range(8)]

def get_main_stylesheet():
    """Returns the main application stylesheet"""
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
    }}
    
    /* Central Widget */
    QWidget {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
        font-size: 10pt;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS['bg_header']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: 500;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['border_light']};
        border: 1px solid {COLORS['text_secondary']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['accent_primary']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_disabled']};
        border: 1px solid {COLORS['bg_tertiary']};
    }}
    
    /* Primary Action Button (Capture) */
    QPushButton#captureBtn {{
        background-color: {COLORS['accent_primary']};
        border: 1px solid {COLORS['accent_primary']};
        color: white;
        font-weight: bold;
        padding: 8px 20px;
    }}
    
    QPushButton#captureBtn:hover {{
        background-color: {COLORS['accent_secondary']};
        border: 1px solid {COLORS['accent_secondary']};
    }}
    
    QPushButton#captureBtn:pressed {{
        background-color: {COLORS['accent_hover']};
        border: 1px solid {COLORS['accent_hover']};
    }}
    
    QPushButton#captureBtn:disabled {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_disabled']};
        border: 1px solid {COLORS['bg_tertiary']};
    }}
    
    /* Connect Button States */
    QPushButton#connectBtn[connected="true"] {{
        background-color: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['success']};
        color: {COLORS['success']};
    }}
    
    /* ComboBox */
    QComboBox {{
        background-color: {COLORS['bg_header']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_light']};
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 120px;
    }}
    
    QComboBox:hover {{
        border: 1px solid {COLORS['text_secondary']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {COLORS['text_secondary']};
        margin-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        selection-background-color: {COLORS['accent_primary']};
        selection-color: white;
        border: 1px solid {COLORS['border_light']};
        outline: 0px;
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['text_primary']};
        background: transparent;
        border: none;
    }}
    
    QLabel#sectionLabel {{
        color: {COLORS['accent_secondary']};
        font-weight: 600;
        font-size: 9pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS['accent_primary']};
        color: white;
        font-weight: bold;
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    
    /* Toolbar Container */
    QWidget#toolbar {{
        background-color: {COLORS['bg_secondary']};
        border-bottom: 1px solid {COLORS['border_light']};
    }}
    
    /* Separator Line */
    QFrame[frameShape="4"] {{  /* VLine */
        background-color: {COLORS['border_light']};
        max-width: 1px;
        border: none;
    }}
    
    QFrame[frameShape="5"] {{  /* HLine */
        background-color: {COLORS['border_light']};
        max-height: 1px;
        border: none;
    }}
    
    /* Sliders */
    QSlider::groove:horizontal {{
        border: 1px solid {COLORS['bg_tertiary']};
        height: 6px;
        background: {COLORS['bg_tertiary']};
        margin: 2px 0;
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: {COLORS['accent_primary']};
        border: 1px solid {COLORS['accent_primary']};
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {COLORS['accent_secondary']};
    }}
    
    /* Scrollbar */
    QScrollBar:horizontal {{
        background: {COLORS['bg_primary']};
        height: 10px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {COLORS['border_light']};
        min-width: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {COLORS['text_secondary']};
    }}
    
    QScrollBar::vertical {{
        background: {COLORS['bg_primary']};
        width: 10px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {COLORS['border_light']};
        min-height: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['text_secondary']};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        border: none;
        background: none;
    }}
    
    /* ToolTip */
    QToolTip {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_light']};
        padding: 4px;
    }}
    """

def get_status_indicator_html(status, text):
    """Generate HTML for status indicator with colored dot"""
    color_map = {
        'connected': COLORS['success'],
        'disconnected': COLORS['text_disabled'],
        'capturing': COLORS['accent_secondary'],
        'error': COLORS['error'],
    }
    
    color = color_map.get(status, COLORS['text_secondary'])
    
    # Professional, minimal status indicator
    return f"""
    <div style='font-family: Consolas, monospace; font-size: 9pt;'>
        <span style='color: {color};'>●</span>
        <span style='color: {COLORS["text_primary"]}; margin-left: 4px;'>{text}</span>
    </div>
    """
