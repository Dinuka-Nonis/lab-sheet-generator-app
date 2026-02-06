"""
Template Selector Dialog for Lab Sheet Generator V2.0.0
Allows users to choose templates with visual previews
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QButtonGroup, QRadioButton, QScrollArea, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from pathlib import Path

from app.core.template_manager import get_template_manager


class TemplatePreviewWidget(QLabel):
    """Widget that shows a preview of the template."""
    
    def __init__(self, template_id, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.setFixedSize(200, 140)
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        
        # Try to load preview image
        preview_path = Path(__file__).parent.parent / "ui" / "assets" / f"{template_id}_preview.png"
        
        if preview_path.exists():
            pixmap = QPixmap(str(preview_path))
            scaled_pixmap = pixmap.scaled(198, 138, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
        else:
            # Generate simple preview
            self.generate_preview()
    
    def generate_preview(self):
        """Generate a simple preview representation."""
        pixmap = QPixmap(200, 140)
        pixmap.fill(QColor("#f8f9fa"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.template_id == "classic":
            # Blue header bar
            painter.fillRect(0, 0, 200, 20, QColor("#156082"))
            
            # Logo placeholder
            painter.setPen(QColor("#d1d5db"))
            painter.drawRect(80, 30, 40, 40)
            painter.drawText(85, 55, "Logo")
            
            # Title lines
            painter.setPen(QColor("#1a1a1a"))
            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.drawText(40, 85, "Module Name - Code")
            
            painter.setFont(QFont("Arial", 6))
            painter.drawText(10, 100, "Practical 01")
            painter.drawText(10, 112, "Student Name - ID")
            
        elif self.template_id == "sliit":
            # Logo top right
            painter.setPen(QColor("#d1d5db"))
            painter.drawRect(150, 10, 40, 30)
            painter.drawText(158, 28, "Logo")
            
            # Large title
            painter.setPen(QColor("#0E2841"))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(10, 60, "Lab 01")
            
            painter.setFont(QFont("Arial", 7, QFont.Bold))
            painter.drawText(10, 75, "Module (CODE)")
            
            # Student info at bottom
            painter.setFont(QFont("Arial", 6))
            painter.drawText(120, 130, "ID - Name")
            
            # Border
            painter.setPen(QColor("#1a1a1a"))
            painter.drawRect(1, 1, 198, 138)
        
        painter.end()
        self.setPixmap(pixmap)


class TemplateCard(QFrame):
    """Widget representing a single template option with preview."""
    
    clicked = Signal(str)  # Emits template ID when clicked
    
    def __init__(self, template_id, template_name, template_description, 
                 is_selected=False, parent=None):
        super().__init__(parent)
        self.template_id = template_id
        self.is_selected = is_selected
        
        self.setFrameStyle(QFrame.Box)
        self.setCursor(Qt.PointingHandCursor)
        
        # Set initial style
        self.update_style()
        
        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Preview
        self.preview = TemplatePreviewWidget(template_id)
        layout.addWidget(self.preview, 0, Qt.AlignCenter)
        
        # Radio button and name in horizontal layout
        header_layout = QHBoxLayout()
        
        self.radio = QRadioButton()
        self.radio.setChecked(is_selected)
        self.radio.toggled.connect(self.on_radio_toggled)
        header_layout.addWidget(self.radio)
        
        name_label = QLabel(template_name)
        name_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Template description
        desc_label = QLabel(template_description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        layout.addWidget(desc_label)
        
        # Font requirements check
        manager = get_template_manager()
        template = manager.get_template(template_id)
        font_status = template.validate_fonts()
        
        if not all(font_status.values()):
            missing_fonts = [font for font, available in font_status.items() if not available]
            warning_label = QLabel(f"⚠️  Missing fonts: {', '.join(missing_fonts)}")
            warning_label.setStyleSheet("color: #f59e0b; font-size: 11px; font-style: italic;")
            warning_label.setWordWrap(True)
            layout.addWidget(warning_label)
        else:
            check_label = QLabel("✓ All fonts available")
            check_label.setStyleSheet("color: #10b981; font-size: 11px;")
            layout.addWidget(check_label)
        
        self.setLayout(layout)
        self.setMinimumHeight(280)
        self.setMaximumHeight(320)
    
    def update_style(self):
        """Update widget style based on selection state."""
        if self.is_selected:
            self.setStyleSheet("""
                TemplateCard {
                    border: 2px solid #5b8def;
                    border-radius: 10px;
                    background-color: #eff6ff;
                }
                TemplateCard:hover {
                    background-color: #dbeafe;
                }
            """)
        else:
            self.setStyleSheet("""
                TemplateCard {
                    border: 1.5px solid #e1e4e8;
                    border-radius: 10px;
                    background-color: white;
                }
                TemplateCard:hover {
                    border: 2px solid #5b8def;
                    background-color: #f9fafb;
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
        self.setMinimumSize(700, 600)
        
        self.selected_template_id = current_template_id
        self.template_cards = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("Choose Document Template")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignLeft)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Select the template design for your lab sheets")
        subtitle.setStyleSheet("color: #6b7280; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignLeft)
        layout.addWidget(subtitle)
        
        # Scroll area for templates
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QHBoxLayout()  # Changed to horizontal for side-by-side cards
        scroll_layout.setSpacing(16)
        
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
        info_label.setStyleSheet("""
            color: #6b7280; 
            font-size: 12px; 
            font-style: italic;
            background-color: #f9fafb;
            padding: 12px;
            border-radius: 6px;
        """)
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("styleClass", "secondary")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("Select Template")
        select_btn.setMinimumWidth(140)
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