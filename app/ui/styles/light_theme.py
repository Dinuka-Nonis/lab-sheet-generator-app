"""
Light Theme Stylesheet for Lab Sheet Generator V2.0.0
Apple-inspired clean design with white background and blue accents
"""


def get_light_theme_stylesheet():
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