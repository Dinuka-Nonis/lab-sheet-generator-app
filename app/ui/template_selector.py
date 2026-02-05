"""
Template Selector Dialog for Lab Sheet Generator V2.0.0
Allows users to choose which template to use for generating documents
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QButtonGroup, QRadioButton, QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from app.core.template_manager import get_template_manager


class TemplateCard(QFrame):
    """Widget representing a single template option."""
    
    clicked = Signal(str)  # Emits template ID when clicked
    
    def __init__(self, template_id, template_name, template_description, 
                 is_selected=False, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.is_selected = is_selected
        
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set initial style
        self.update_style()
        
        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Radio button for selection
        self.radio = QRadioButton()
        self.radio.setChecked(is_selected)
        self.radio.toggled.connect(self.on_radio_toggled)
        
        # Template name
        name_label = QLabel(template_name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Template description
        desc_label = QLabel(template_description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray; font-size: 12px;")
        
        # Font requirements check
        manager = get_template_manager()
        template = manager.get_template(template_id)
        font_status = template.validate_fonts()
        
        if not all(font_status.values()):
            missing_fonts = [font for font, available in font_status.items() if not available]
            warning_label = QLabel(f"⚠️  Missing fonts: {', '.join(missing_fonts)}")
            warning_label.setStyleSheet("color: #ff9500; font-size: 11px; font-style: italic;")
            warning_label.setWordWrap(True)
        else:
            warning_label = QLabel("✓ All fonts available")
            warning_label.setStyleSheet("color: green; font-size: 11px;")
        
        # Add widgets to layout
        layout.addWidget(self.radio)
        layout.addWidget(name_label)
        layout.addWidget(desc_label)
        layout.addWidget(warning_label)
        
        self.setLayout(layout)
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)
    
    def update_style(self):
        """Update widget style based on selection state."""
        if self.is_selected:
            self.setStyleSheet("""
                TemplateCard {
                    border: 2px solid #007aff;
                    border-radius: 8px;
                    background-color: rgba(0, 122, 255, 0.05);
                    padding: 12px;
                }
                TemplateCard:hover {
                    background-color: rgba(0, 122, 255, 0.1);
                }
            """)
        else:
            self.setStyleSheet("""
                TemplateCard {
                    border: 1.5px solid #d2d2d7;
                    border-radius: 8px;
                    background-color: transparent;
                    padding: 12px;
                }
                TemplateCard:hover {
                    border: 2px solid #007aff;
                    background-color: rgba(0, 122, 255, 0.02);
                }
            """)
    
    def on_radio_toggled(self, checked):
        """Handle radio button toggle."""
        if checked:
            self.is_selected = True
            self.update_style()
            self.clicked.emit(self.template_id)
    
    def set_selected(self, selected):
        """Set selection state."""
        self.is_selected = selected
        self.radio.setChecked(selected)
        self.update_style()
    
    def mousePressEvent(self, event):
        """Handle mouse click on card."""
        self.radio.setChecked(True)
        super().mousePressEvent(event)


class TemplateSelectorDialog(QDialog):
    """Dialog for selecting a document template."""
    
    def __init__(self, current_template_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Template")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        self.selected_template_id = current_template_id
        self.template_cards = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Choose Document Template")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Select the template you want to use for generating lab sheets")
        subtitle.setStyleSheet("color: gray; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Scroll area for templates
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(12)
        
        # Get available templates
        manager = get_template_manager()
        templates = manager.get_template_list()
        
        # Create button group for radio buttons
        self.button_group = QButtonGroup()
        
        # Create template cards
        for i, template_info in enumerate(templates):
            template_id = template_info['id']
            is_selected = (template_id == self.selected_template_id)
            
            card = TemplateCard(
                template_id,
                template_info['name'],
                template_info['description'],
                is_selected
            )
            card.clicked.connect(self.on_template_selected)
            
            self.button_group.addButton(card.radio, i)
            self.template_cards[template_id] = card
            
            scroll_layout.addWidget(card)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        
        layout.addWidget(scroll, 1)
        
        # Info message
        info_label = QLabel(
            "💡 Tip: Templates may require specific fonts. If fonts are missing, "
            "the document will use system defaults which may affect appearance."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 11px; font-style: italic;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("styleClass", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("Select Template")
        select_btn.clicked.connect(self.accept)
        select_btn.setDefault(True)
        button_layout.addWidget(select_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_template_selected(self, template_id):
        """Handle template selection."""
        self.selected_template_id = template_id
        
        # Update all cards to reflect selection
        for tid, card in self.template_cards.items():
            card.set_selected(tid == template_id)
    
    def get_selected_template(self):
        """Get the selected template ID."""
        return self.selected_template_id


def show_template_selector(current_template_id=None, parent=None):
    """
    Show template selector dialog and return selected template.
    
    Args:
        current_template_id: Currently selected template
        parent: Parent widget
        
    Returns:
        str or None: Selected template ID, or None if cancelled
    """
    dialog = TemplateSelectorDialog(current_template_id, parent)
    if dialog.exec():
        return dialog.get_selected_template()
    return None