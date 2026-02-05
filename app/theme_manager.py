"""
Theme Manager for Lab Sheet Generator V2.0.0
Provides light and dark theme support with Apple-like modern design
"""

from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

class ThemeManager:
    """Manages application themes with modern, clean styling."""
    
    LIGHT_THEME = "light"
    DARK_THEME = "dark"
    
    def __init__(self):
        self.current_theme = self.LIGHT_THEME
    
    def get_light_theme_stylesheet(self):
        """Get light theme stylesheet with Apple-like design."""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #f5f5f7;
        }
        
        QWidget {
            background-color: #f5f5f7;
            color: #1d1d1f;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
            font-size: 13px;
        }
        
        /* Group Boxes */
        QGroupBox {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 12px;
            margin-top: 12px;
            padding: 20px;
            font-weight: 600;
            font-size: 14px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: #1d1d1f;
        }
        
        /* Labels */
        QLabel {
            background-color: transparent;
            color: #1d1d1f;
        }
        
        /* Line Edits */
        QLineEdit {
            background-color: #ffffff;
            border: 1.5px solid #d2d2d7;
            border-radius: 8px;
            padding: 8px 12px;
            color: #1d1d1f;
            selection-background-color: #007aff;
            selection-color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 2px solid #007aff;
            background-color: #ffffff;
        }
        
        QLineEdit:disabled {
            background-color: #f5f5f7;
            color: #86868b;
        }
        
        /* Combo Boxes */
        QComboBox {
            background-color: #ffffff;
            border: 1.5px solid #d2d2d7;
            border-radius: 8px;
            padding: 8px 12px;
            color: #1d1d1f;
        }
        
        QComboBox:focus {
            border: 2px solid #007aff;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #86868b;
            margin-right: 8px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 8px;
            selection-background-color: #007aff;
            selection-color: #ffffff;
            padding: 4px;
        }
        
        /* Spin Boxes */
        QSpinBox {
            background-color: #ffffff;
            border: 1.5px solid #d2d2d7;
            border-radius: 8px;
            padding: 8px 12px;
            color: #1d1d1f;
        }
        
        QSpinBox:focus {
            border: 2px solid #007aff;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: transparent;
            border: none;
            width: 20px;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #007aff;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        
        QPushButton:hover {
            background-color: #0051d5;
        }
        
        QPushButton:pressed {
            background-color: #004fc4;
        }
        
        QPushButton:disabled {
            background-color: #d2d2d7;
            color: #86868b;
        }
        
        /* Secondary Buttons */
        QPushButton[styleClass="secondary"] {
            background-color: #e8e8ed;
            color: #1d1d1f;
        }
        
        QPushButton[styleClass="secondary"]:hover {
            background-color: #d2d2d7;
        }
        
        QPushButton[styleClass="secondary"]:pressed {
            background-color: #c7c7cc;
        }
        
        /* Danger Buttons */
        QPushButton[styleClass="danger"] {
            background-color: #ff3b30;
            color: #ffffff;
        }
        
        QPushButton[styleClass="danger"]:hover {
            background-color: #ff2d20;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #ffffff;
            border: 1.5px solid #d2d2d7;
            border-radius: 8px;
            padding: 4px;
            color: #1d1d1f;
        }
        
        QListWidget::item {
            padding: 10px;
            border-radius: 6px;
        }
        
        QListWidget::item:selected {
            background-color: #007aff;
            color: #ffffff;
        }
        
        QListWidget::item:hover {
            background-color: #f5f5f7;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #f5f5f7;
            color: #1d1d1f;
            border-bottom: 1px solid #d2d2d7;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 6px;
        }
        
        QMenuBar::item:selected {
            background-color: #e8e8ed;
        }
        
        QMenu {
            background-color: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 8px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 24px;
            border-radius: 6px;
        }
        
        QMenu::item:selected {
            background-color: #007aff;
            color: #ffffff;
        }
        
        /* Scroll Bars */
        QScrollBar:vertical {
            background-color: transparent;
            width: 12px;
            margin: 0;
        }
        
        QScrollBar::handle:vertical {
            background-color: #c7c7cc;
            border-radius: 6px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #86868b;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #f5f5f7;
            color: #1d1d1f;
            border-top: 1px solid #d2d2d7;
        }
        
        /* Tool Tips */
        QToolTip {
            background-color: #1d1d1f;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
        }
        """
    
    def get_dark_theme_stylesheet(self):
        """Get dark theme stylesheet with Apple-like design."""
        return """
        /* Main Window */
        QMainWindow {
            background-color: #1c1c1e;
        }
        
        QWidget {
            background-color: #1c1c1e;
            color: #f5f5f7;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
            font-size: 13px;
        }
        
        /* Group Boxes */
        QGroupBox {
            background-color: #2c2c2e;
            border: 1px solid #38383a;
            border-radius: 12px;
            margin-top: 12px;
            padding: 20px;
            font-weight: 600;
            font-size: 14px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
            color: #f5f5f7;
        }
        
        /* Labels */
        QLabel {
            background-color: transparent;
            color: #f5f5f7;
        }
        
        /* Line Edits */
        QLineEdit {
            background-color: #2c2c2e;
            border: 1.5px solid #38383a;
            border-radius: 8px;
            padding: 8px 12px;
            color: #f5f5f7;
            selection-background-color: #0a84ff;
            selection-color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 2px solid #0a84ff;
            background-color: #2c2c2e;
        }
        
        QLineEdit:disabled {
            background-color: #1c1c1e;
            color: #636366;
        }
        
        /* Combo Boxes */
        QComboBox {
            background-color: #2c2c2e;
            border: 1.5px solid #38383a;
            border-radius: 8px;
            padding: 8px 12px;
            color: #f5f5f7;
        }
        
        QComboBox:focus {
            border: 2px solid #0a84ff;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        
        QComboBox::down-arrow {
            image: url(none);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #98989d;
            margin-right: 8px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2c2c2e;
            border: 1px solid #38383a;
            border-radius: 8px;
            selection-background-color: #0a84ff;
            selection-color: #ffffff;
            padding: 4px;
        }
        
        /* Spin Boxes */
        QSpinBox {
            background-color: #2c2c2e;
            border: 1.5px solid #38383a;
            border-radius: 8px;
            padding: 8px 12px;
            color: #f5f5f7;
        }
        
        QSpinBox:focus {
            border: 2px solid #0a84ff;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: transparent;
            border: none;
            width: 20px;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #0a84ff;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        
        QPushButton:hover {
            background-color: #0077ed;
        }
        
        QPushButton:pressed {
            background-color: #006edb;
        }
        
        QPushButton:disabled {
            background-color: #38383a;
            color: #636366;
        }
        
        /* Secondary Buttons */
        QPushButton[styleClass="secondary"] {
            background-color: #38383a;
            color: #f5f5f7;
        }
        
        QPushButton[styleClass="secondary"]:hover {
            background-color: #48484a;
        }
        
        QPushButton[styleClass="secondary"]:pressed {
            background-color: #58585a;
        }
        
        /* Danger Buttons */
        QPushButton[styleClass="danger"] {
            background-color: #ff453a;
            color: #ffffff;
        }
        
        QPushButton[styleClass="danger"]:hover {
            background-color: #ff3b30;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #2c2c2e;
            border: 1.5px solid #38383a;
            border-radius: 8px;
            padding: 4px;
            color: #f5f5f7;
        }
        
        QListWidget::item {
            padding: 10px;
            border-radius: 6px;
        }
        
        QListWidget::item:selected {
            background-color: #0a84ff;
            color: #ffffff;
        }
        
        QListWidget::item:hover {
            background-color: #38383a;
        }
        
        /* Menu Bar */
        QMenuBar {
            background-color: #1c1c1e;
            color: #f5f5f7;
            border-bottom: 1px solid #38383a;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 6px;
        }
        
        QMenuBar::item:selected {
            background-color: #2c2c2e;
        }
        
        QMenu {
            background-color: #2c2c2e;
            border: 1px solid #38383a;
            border-radius: 8px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 24px;
            border-radius: 6px;
        }
        
        QMenu::item:selected {
            background-color: #0a84ff;
            color: #ffffff;
        }
        
        /* Scroll Bars */
        QScrollBar:vertical {
            background-color: transparent;
            width: 12px;
            margin: 0;
        }
        
        QScrollBar::handle:vertical {
            background-color: #48484a;
            border-radius: 6px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #636366;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Status Bar */
        QStatusBar {
            background-color: #1c1c1e;
            color: #f5f5f7;
            border-top: 1px solid #38383a;
        }
        
        /* Tool Tips */
        QToolTip {
            background-color: #f5f5f7;
            color: #1d1d1f;
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
        }
        """
    
    def get_stylesheet(self, theme=None):
        """Get stylesheet for specified theme."""
        if theme is None:
            theme = self.current_theme
        
        if theme == self.DARK_THEME:
            return self.get_dark_theme_stylesheet()
        else:
            return self.get_light_theme_stylesheet()
    
    def set_theme(self, theme):
        """Set current theme."""
        if theme in [self.LIGHT_THEME, self.DARK_THEME]:
            self.current_theme = theme
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        if self.current_theme == self.LIGHT_THEME:
            self.current_theme = self.DARK_THEME
        else:
            self.current_theme = self.LIGHT_THEME
        return self.current_theme
    
    def get_current_theme(self):
        """Get current theme name."""
        return self.current_theme