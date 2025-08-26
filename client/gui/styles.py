"""
Modern Dark Theme Styles for Group Change Params
"""

# Main window style with dark theme
MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QMenuBar {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border-bottom: 1px solid #3c3c3c;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #404040;
}

QMenu {
    background-color: #2b2b2b;
    color: #e0e0e0;
    border: 1px solid #3c3c3c;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #404040;
}

QStatusBar {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border-top: 1px solid #3c3c3c;
    padding: 4px;
}
"""

# Tab widget styles
TAB_STYLE = """
QTabWidget::pane {
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    background-color: #2b2b2b;
    padding: 4px;
}

QTabBar::tab {
    background-color: #1e1e1e;
    color: #b0b0b0;
    padding: 12px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #3c3c3c;
    border-bottom: none;
    min-width: 120px;
}

QTabBar::tab:selected {
    background-color: #2b2b2b;
    color: #e0e0e0;
    border-bottom: 2px solid #0078d4;
}

QTabBar::tab:hover:!selected {
    background-color: #404040;
    color: #e0e0e0;
}
"""

# Group box styles
GROUP_BOX_STYLE = """
QGroupBox {
    font-weight: bold;
    border: 2px solid #3c3c3c;
    border-radius: 8px;
    margin-top: 1ex;
    padding-top: 10px;
    background-color: #323232;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
    color: #0078d4;
    font-size: 11pt;
    font-weight: bold;
}
"""

# Button styles
BUTTON_STYLES = {
    "primary": """
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 10pt;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
        }
    """,
    "secondary": """
        QPushButton {
            background-color: #404040;
            color: #e0e0e0;
            border: 1px solid #5c5c5c;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 10pt;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
            border-color: #6c6c6c;
        }
        QPushButton:pressed {
            background-color: #363636;
        }
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #606060;
            border-color: #404040;
        }
    """,
    "success": """
        QPushButton {
            background-color: #107c10;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 10pt;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #0e6a0e;
        }
        QPushButton:pressed {
            background-color: #0c590c;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
        }
    """,
    "warning": """
        QPushButton {
            background-color: #ff8c00;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 10pt;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #e67e00;
        }
        QPushButton:pressed {
            background-color: #cc7000;
        }
        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
        }
    """
}

# Input controls styles
INPUT_STYLE = """
QLineEdit, QSpinBox, QComboBox {
    background-color: #404040;
    color: #e0e0e0;
    border: 1px solid #5c5c5c;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 10pt;
    min-height: 16px;
}

QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #0078d4;
    background-color: #454545;
}

QComboBox::drop-down {
    border: none;
    background-color: transparent;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #404040;
    color: #e0e0e0;
    border: 1px solid #5c5c5c;
    border-radius: 6px;
    selection-background-color: #0078d4;
    padding: 4px;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #5c5c5c;
    border: none;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #6c6c6c;
}
"""

# Checkbox styles
CHECKBOX_STYLE = """
QCheckBox {
    color: #e0e0e0;
    font-size: 10pt;
    spacing: 6px;
    margin: 0px;
    padding: 2px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #5c5c5c;
    border-radius: 4px;
    background-color: #404040;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
}

QCheckBox::indicator:hover {
    border-color: #0078d4;
}
"""

# Dialog button styles
DIALOG_BUTTON_STYLE = """
QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 9pt;
    min-width: 60px;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #106ebe;
}
QPushButton:pressed {
    background-color: #005a9e;
}
QPushButton:default {
    background-color: #0078d4;
    border: 2px solid #005a9e;
}
"""

# List widget styles
LIST_STYLE = """
QListWidget {
    background-color: #404040;
    color: #e0e0e0;
    border: 1px solid #5c5c5c;
    border-radius: 6px;
    padding: 4px;
    font-size: 10pt;
}

QListWidget::item {
    padding: 6px 12px;
    border-radius: 4px;
    margin: 1px;
}

QListWidget::item:selected {
    background-color: #0078d4;
    color: white;
}

QListWidget::item:hover:!selected {
    background-color: #4a4a4a;
}
"""

# Label styles
LABEL_STYLES = {
    "title": """
        QLabel {
            color: #0078d4;
            font-size: 14pt;
            font-weight: bold;
            padding: 8px 0px;
        }
    """,
    "subtitle": """
        QLabel {
            color: #e0e0e0;
            font-size: 11pt;
            font-weight: bold;
            padding: 4px 0px;
        }
    """,
    "info": """
        QLabel {
            color: #b0b0b0;
            font-size: 10pt;
            padding: 4px 8px;
            background-color: #3a3a3a;
            border: 1px solid #4a4a4a;
            border-radius: 4px;
        }
    """,
    "success": """
        QLabel {
            color: #4BB543;
            font-size: 10pt;
            font-weight: bold;
        }
    """,
    "error": """
        QLabel {
            color: #ff4444;
            font-size: 10pt;
            font-weight: bold;
        }
    """
}

# Progress bar style
PROGRESS_STYLE = """
QProgressBar {
    border: 1px solid #5c5c5c;
    border-radius: 6px;
    text-align: center;
    background-color: #404040;
    color: #e0e0e0;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 5px;
}
"""
