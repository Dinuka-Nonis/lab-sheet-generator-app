"""
Theme Manager for Lab Sheet Generator V2.0.0
Modern, clean light theme with Helvetica-style fonts and proper sizing
"""


class ThemeManager:
    """Manages application theme with modern, clean styling."""
    
    def __init__(self):
        self.current_theme = "light"
    
    def get_stylesheet(self):
        """Get the application stylesheet with modern fonts."""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #fafbfc;
        }
        
        QWidget {
            background-color: #fafbfc;
            color: #1a1a1a;
            font-family: "Segoe UI", "Helvetica Neue", "Helvetica", Arial, sans-serif;
            font-size: 14px;
        }
        
        /* Group Boxes - Card Style */
        QGroupBox {
            background-color: #ffffff;
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            margin-top: 20px;
            padding: 24px;
            font-weight: 600;
            font-size: 15px;
            color: #24292e;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 0 10px;
            color: #24292e;
            background-color: #ffffff;
        }
        
        /* Labels */
        QLabel {
            background-color: transparent;
            color: #24292e;
            font-size: 14px;
        }
        
        /* Form Labels */
        QFormLayout QLabel {
            font-size: 14px;
            font-weight: 500;
            color: #586069;
        }
        
        /* Line Edits */
        QLineEdit {
            background-color: #ffffff;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            padding: 10px 14px;
            color: #24292e;
            selection-background-color: #5b8def;
            selection-color: #ffffff;
            font-size: 14px;
        }
        
        QLineEdit:focus {
            border: 2px solid #5b8def;
            background-color: #ffffff;
        }
        
        QLineEdit:disabled {
            background-color: #f6f8fa;
            color: #959da5;
            border-color: #e1e4e8;
        }
        
        /* Combo Boxes */
        QComboBox {
            background-color: #ffffff;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            padding: 10px 14px;
            color: #24292e;
            font-size: 14px;
        }
        
        QComboBox:focus {
            border: 2px solid #5b8def;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 32px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 7px solid #586069;
            margin-right: 10px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #d1d5da;
            border-radius: 8px;
            selection-background-color: #5b8def;
            selection-color: #ffffff;
            padding: 6px;
            outline: none;
            font-size: 14px;
        }
        
        QComboBox QAbstractItemView::item {
            padding: 8px 12px;
            min-height: 28px;
        }
        
        /* Spin Boxes */
        QSpinBox {
            background-color: #ffffff;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            padding: 10px 14px;
            color: #24292e;
            font-size: 14px;
        }
        
        QSpinBox:focus {
            border: 2px solid #5b8def;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: transparent;
            border: none;
            width: 24px;
        }
        
        /* Buttons - Primary */
        QPushButton {
            background-color: #5b8def;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
        }
        
        QPushButton:hover {
            background-color: #4a7de8;
        }
        
        QPushButton:pressed {
            background-color: #3a6dd7;
        }
        
        QPushButton:disabled {
            background-color: #d1d5da;
            color: #959da5;
        }
        
        /* Secondary Buttons */
        QPushButton[styleClass="secondary"] {
            background-color: #ffffff;
            color: #24292e;
            border: 2px solid #d1d5da;
            font-weight: 500;
        }
        
        QPushButton[styleClass="secondary"]:hover {
            background-color: #f6f8fa;
            border-color: #959da5;
        }
        
        QPushButton[styleClass="secondary"]:pressed {
            background-color: #e1e4e8;
        }
        
        /* Danger Buttons */
        QPushButton[styleClass="danger"] {
            background-color: #d73a49;
            color: #ffffff;
        }
        
        QPushButton[styleClass="danger"]:hover {
            background-color: #cb2431;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #ffffff;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            padding: 8px;
            color: #24292e;
            font-size: 14px;
        }
        
        QListWidget::item {
            padding: 12px;
            border-radius: 6px;
            margin: 2px 0;
            min-height: 20px;
        }
        
        QListWidget::item:selected {
            background-color: #f1f8ff;
            color: #24292e;
            border: 1px solid #5b8def;
        }
        
        QListWidget::item:hover {
            background-color: #f6f8fa;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #ffffff;
            color: #24292e;
            border-bottom: 1px solid #e1e4e8;
            padding: 6px;
            font-size: 14px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 16px;
            border-radius: 6px;
        }
        
        QMenuBar::item:selected {
            background-color: #f6f8fa;
        }
        
        QMenu {
            background-color: #ffffff;
            border: 1px solid #d1d5da;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
        }
        
        QMenu::item {
            padding: 10px 30px;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QMenu::item:selected {
            background-color: #f1f8ff;
            color: #24292e;
        }
        
        /* Scroll Bars */
        QScrollBar:vertical {
            background-color: transparent;
            width: 12px;
            margin: 0;
        }
        
        QScrollBar::handle:vertical {
            background-color: #d1d5da;
            border-radius: 6px;
            min-height: 40px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #959da5;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #fafbfc;
            color: #24292e;
            border-top: 1px solid #e1e4e8;
            font-size: 13px;
        }
        
        /* Tool Tips */
        QToolTip {
            background-color: #24292e;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }
        
        /* Dialog Buttons */
        QDialogButtonBox QPushButton {
            min-width: 90px;
        }
        """