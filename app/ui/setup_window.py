from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFileDialog, QMessageBox, QListWidget, 
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QComboBox,
    QTabWidget, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPalette, QColor
from app.utils.validators import (
    validate_student_name, validate_student_id, 
    validate_module_name, validate_module_code
)
from app.core.template_manager import get_template_manager


class ModuleDialog(QDialog):
    """Dialog for adding/editing a module."""
    
    def __init__(self, parent=None, module_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add Module" if not module_data else "Edit Module")
        self.setModal(True)
        self.setMinimumWidth(540)
        
        layout = QFormLayout()
        layout.setSpacing(18)
        
        # Module name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Programming Paradigms")
        self.name_input.setMinimumHeight(44)
        self.name_input.setStyleSheet("font-size: 15px;")
        layout.addRow("<b style='font-size: 15px;'>Module Name:</b>", self.name_input)
        
        # Module code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g., SE2052")
        self.code_input.setMaxLength(10)
        self.code_input.setMinimumHeight(44)
        self.code_input.setStyleSheet("font-size: 15px;")
        layout.addRow("<b style='font-size: 15px;'>Module Code:</b>", self.code_input)
        
        # Sheet type
        self.sheet_type_combo = QComboBox()
        self.sheet_type_combo.setMinimumHeight(44)
        self.sheet_type_combo.setStyleSheet("font-size: 15px;")
        self.sheet_type_combo.addItems([
            "Practical", "Lab", "Worksheet", "Tutorial",
            "Assignment", "Exercise", "Custom"
        ])
        self.sheet_type_combo.currentTextChanged.connect(self.on_sheet_type_changed)
        layout.addRow("<b style='font-size: 15px;'>Sheet Type:</b>", self.sheet_type_combo)
        
        # Custom type (hidden by default)
        self.custom_type_input = QLineEdit()
        self.custom_type_input.setPlaceholderText("e.g., Problem Set")
        self.custom_type_input.setMinimumHeight(44)
        self.custom_type_input.setStyleSheet("font-size: 15px;")
        self.custom_type_input.setVisible(False)
        self.custom_type_label = QLabel("<b style='font-size: 15px;'>Custom Type:</b>")
        self.custom_type_label.setVisible(False)
        layout.addRow(self.custom_type_label, self.custom_type_input)
        
        # Template
        self.template_combo = QComboBox()
        self.template_combo.setMinimumHeight(44)
        self.template_combo.setStyleSheet("font-size: 15px;")
        manager = get_template_manager()
        for template in manager.get_template_list():
            self.template_combo.addItem(template['name'], template['id'])
        layout.addRow("<b style='font-size: 15px;'>Template:</b>", self.template_combo)
        
        # Output path
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Leave empty for default")
        self.path_input.setMinimumHeight(44)
        self.path_input.setStyleSheet("font-size: 14px;")
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setProperty("styleClass", "secondary")
        browse_btn.setMinimumHeight(42)
        browse_btn.setStyleSheet("font-size: 14px; font-weight: 600;")
        browse_btn.clicked.connect(self.browse_output_path)
        path_layout.addWidget(browse_btn)
        
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        layout.addRow("<b style='font-size: 15px;'>Output Path:</b>", path_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
        
        self.setLayout(layout)
        
        if module_data:
            self.load_module_data(module_data)
    
    def load_module_data(self, module_data):
        """Load existing module data."""
        self.name_input.setText(module_data.get('name', ''))
        self.code_input.setText(module_data.get('code', ''))
        
        sheet_type = module_data.get('sheet_type', 'Practical')
        index = self.sheet_type_combo.findText(sheet_type)
        if index >= 0:
            self.sheet_type_combo.setCurrentIndex(index)
        
        if module_data.get('custom_sheet_type'):
            self.custom_type_input.setText(module_data['custom_sheet_type'])
        
        template_id = module_data.get('template', 'classic')
        template_index = self.template_combo.findData(template_id)
        if template_index >= 0:
            self.template_combo.setCurrentIndex(template_index)
        
        if module_data.get('output_path'):
            self.path_input.setText(module_data['output_path'])
    
    def on_sheet_type_changed(self, text):
        """Show/hide custom type input."""
        is_custom = text == "Custom"
        self.custom_type_input.setVisible(is_custom)
        self.custom_type_label.setVisible(is_custom)
        self.adjustSize()
    
    def browse_output_path(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.path_input.text() or ""
        )
        if folder:
            self.path_input.setText(folder)
    
    def validate_and_accept(self):
        """Validate inputs."""
        name = self.name_input.text().strip()
        code = self.code_input.text().strip().upper()
        
        is_valid, error = validate_module_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return
        
        is_valid, error = validate_module_code(code)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return
        
        if self.sheet_type_combo.currentText() == "Custom" and not self.custom_type_input.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter a custom sheet type")
            return
        
        self.accept()
    
    def get_module(self):
        """Get module data."""
        sheet_type = self.sheet_type_combo.currentText()
        return {
            'name': self.name_input.text().strip(),
            'code': self.code_input.text().strip().upper(),
            'sheet_type': sheet_type,
            'custom_sheet_type': self.custom_type_input.text().strip() if sheet_type == "Custom" else None,
            'output_path': self.path_input.text().strip() or None,
            'use_zero_padding': True,
            'template': self.template_combo.currentData()
        }


class SetupWindow(QWidget):
    """Setup/Edit configuration window with template-specific logos."""
    
    setup_complete = Signal(dict)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.Window)
        
        # Set white background
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        self.setPalette(palette)
        
        self.config = config
        self.template_logos = {}  # Store logos per template: {template_id: path}
        self.modules = []
        
        self.setWindowTitle("Edit Configuration")
        self.setMinimumSize(740, 700)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI with tabs for student info and template logos."""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(28, 28, 28, 28)
        
        # Title
        title = QLabel("Edit Configuration")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: 700; 
            color: #1a1a1a;
            letter-spacing: -0.5px;
        """)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Update your settings and logos")
        subtitle.setStyleSheet("font-size: 16px; color: #586069;")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Tabs for organization
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                padding: 12px 24px;
                font-size: 15px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #5b8def;
                color: white;
            }
        """)
        
        # Student Info Tab
        student_tab = QWidget()
        student_layout = QVBoxLayout()
        student_layout.setSpacing(18)
        
        student_form = QFormLayout()
        student_form.setSpacing(16)
        
        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(44)
        self.name_input.setStyleSheet("font-size: 15px;")
        student_form.addRow("<b style='font-size: 15px;'>Full Name:</b>", self.name_input)
        
        self.id_input = QLineEdit()
        self.id_input.setMinimumHeight(44)
        self.id_input.setStyleSheet("font-size: 15px;")
        student_form.addRow("<b style='font-size: 15px;'>Student ID:</b>", self.id_input)
        
        student_layout.addLayout(student_form)
        student_tab.setLayout(student_layout)
        tabs.addTab(student_tab, "Student Info")
        
        # Logos Tab (NEW!)
        logos_tab = QWidget()
        logos_layout = QVBoxLayout()
        logos_layout.setSpacing(18)
        
        logo_info = QLabel(
            "💡 Tip: Each template can have its own logo. "
            "This allows you to use different university logos for different templates."
        )
        logo_info.setWordWrap(True)
        logo_info.setStyleSheet("""
            font-size: 14px; 
            color: #586069; 
            background: #f6f8fa; 
            padding: 14px; 
            border-radius: 8px;
        """)
        logos_layout.addWidget(logo_info)
        
        # Create logo selector for each template
        self.logo_widgets = {}
        manager = get_template_manager()
        
        for template_info in manager.get_template_list():
            template_id = template_info['id']
            template_name = template_info['name']
            
            logo_group = QGroupBox(f"{template_name} Logo")
            logo_group.setStyleSheet("QGroupBox { font-size: 15px; font-weight: 600; }")
            logo_group_layout = QHBoxLayout()
            
            btn_layout = QVBoxLayout()
            select_btn = QPushButton(f"Select Logo for {template_name}")
            select_btn.setMinimumHeight(42)
            select_btn.setStyleSheet("font-size: 14px; font-weight: 600;")
            select_btn.clicked.connect(lambda checked, tid=template_id: self.select_template_logo(tid))
            btn_layout.addWidget(select_btn)
            
            label = QLabel("No logo selected")
            label.setStyleSheet("font-size: 13px; color: #586069;")
            label.setWordWrap(True)
            btn_layout.addWidget(label)
            btn_layout.addStretch()
            
            logo_group_layout.addLayout(btn_layout, 1)
            
            preview = QLabel()
            preview.setFixedSize(110, 105)
            preview.setStyleSheet("""
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                background-color: #f6f8fa;
            """)
            preview.setAlignment(Qt.AlignCenter)
            preview.setText("Preview")
            logo_group_layout.addWidget(preview)
            
            logo_group.setLayout(logo_group_layout)
            logos_layout.addWidget(logo_group)
            
            self.logo_widgets[template_id] = {'label': label, 'preview': preview}
        
        logos_layout.addStretch()
        logos_tab.setLayout(logos_layout)
        tabs.addTab(logos_tab, "Template Logos")
        
        # Modules Tab
        modules_tab = QWidget()
        modules_layout = QVBoxLayout()
        modules_layout.setSpacing(16)
        
        self.module_list = QListWidget()
        self.module_list.setMinimumHeight(160)
        self.module_list.setStyleSheet("QListWidget { font-size: 14px; }")
        modules_layout.addWidget(self.module_list)
        
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Module")
        add_btn.setMinimumHeight(44)
        add_btn.setStyleSheet("font-size: 15px; font-weight: 600;")
        add_btn.clicked.connect(self.add_module)
        btn_layout.addWidget(add_btn)
        
        self.edit_btn = QPushButton("Edit Module")
        self.edit_btn.setProperty("styleClass", "secondary")
        self.edit_btn.setMinimumHeight(44)
        self.edit_btn.setStyleSheet("font-size: 15px; font-weight: 600;")
        self.edit_btn.clicked.connect(self.edit_module)
        self.edit_btn.setEnabled(False)
        btn_layout.addWidget(self.edit_btn)
        
        self.remove_btn = QPushButton("Remove Module")
        self.remove_btn.setProperty("styleClass", "danger")
        self.remove_btn.setMinimumHeight(44)
        self.remove_btn.setStyleSheet("font-size: 15px; font-weight: 600;")
        self.remove_btn.clicked.connect(self.remove_module)
        self.remove_btn.setEnabled(False)
        btn_layout.addWidget(self.remove_btn)
        
        btn_layout.addStretch()
        modules_layout.addLayout(btn_layout)
        
        modules_tab.setLayout(modules_layout)
        tabs.addTab(modules_tab, "Modules")
        
        main_layout.addWidget(tabs)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("styleClass", "secondary")
        cancel_btn.setMinimumWidth(120)
        cancel_btn.setMinimumHeight(48)
        cancel_btn.setStyleSheet("font-size: 15px; font-weight: 600;")
        cancel_btn.clicked.connect(self.close)
        bottom_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setMinimumWidth(160)
        save_btn.setMinimumHeight(48)
        save_btn.setStyleSheet("font-size: 16px; font-weight: 700;")
        save_btn.clicked.connect(self.save_changes)
        bottom_layout.addWidget(save_btn)
        
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        
        self.module_list.itemSelectionChanged.connect(self.on_selection_changed)
    
    def select_template_logo(self, template_id):
        """Select logo for specific template."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Select Logo", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.template_logos[template_id] = file_path
            
            import os
            widgets = self.logo_widgets[template_id]
            widgets['label'].setText(os.path.basename(file_path))
            widgets['label'].setStyleSheet("color: #28a745; font-weight: 600; font-size: 13px;")
            
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(108, 103, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            widgets['preview'].setPixmap(scaled)
    
    def load_logos_from_config(self, config):
        """Load existing logos for each template."""
        manager = get_template_manager()
        
        for template_info in manager.get_template_list():
            template_id = template_info['id']
            logo_path = config.config_dir / f"logo_{template_id}.png"
            
            if logo_path.exists():
                self.template_logos[template_id] = str(logo_path)
                
                widgets = self.logo_widgets[template_id]
                widgets['label'].setText(logo_path.name)
                widgets['label'].setStyleSheet("color: #28a745; font-weight: 600; font-size: 13px;")
                
                pixmap = QPixmap(str(logo_path))
                scaled = pixmap.scaled(108, 103, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                widgets['preview'].setPixmap(scaled)
    
    def add_module(self):
        """Add new module."""
        dialog = ModuleDialog(self)
        if dialog.exec():
            self.modules.append(dialog.get_module())
            self.update_module_list()
    
    def edit_module(self):
        """Edit selected module."""
        row = self.module_list.currentRow()
        if row >= 0:
            dialog = ModuleDialog(self, self.modules[row])
            if dialog.exec():
                self.modules[row] = dialog.get_module()
                self.update_module_list()
    
    def remove_module(self):
        """Remove selected module."""
        row = self.module_list.currentRow()
        if row >= 0:
            module = self.modules[row]
            reply = QMessageBox.question(
                self, "Remove Module",
                f"Remove '{module['name']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.modules.pop(row)
                self.update_module_list()
    
    def update_module_list(self):
        """Update module list display."""
        self.module_list.clear()
        
        for module in self.modules:
            try:
                sheet_type = module.get('sheet_type', 'Practical')
                if sheet_type == 'Custom':
                    sheet_type = module.get('custom_sheet_type', 'Custom')
                
                template_id = module.get('template', 'classic')
                try:
                    manager = get_template_manager()
                    template = manager.get_template(template_id)
                    template_name = template.template_name
                except:
                    template_name = template_id.title()
                
                path_marker = " 📁" if module.get('output_path') else ""
                text = f"{module['name']} ({module['code']}) - {sheet_type} [{template_name}]{path_marker}"
                self.module_list.addItem(text)
            except Exception as e:
                print(f"ERROR displaying module: {e}")
                self.module_list.addItem(f"{module.get('name', 'Unknown')} - Error")
    
    def on_selection_changed(self):
        """Handle selection change."""
        has_selection = self.module_list.currentRow() >= 0
        self.edit_btn.setEnabled(has_selection)
        self.remove_btn.setEnabled(has_selection)
    
    def save_changes(self):
        """Save configuration with template-specific logos."""
        name = self.name_input.text().strip()
        student_id = self.id_input.text().strip()
        
        is_valid, error = validate_student_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", f"Name: {error}")
            return
        
        is_valid, error = validate_student_id(student_id)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", f"ID: {error}")
            return
        
        # Save config
        self.config.save_config(
            name, student_id, self.modules,
            theme='light', default_template='classic'
        )
        
        # Save template-specific logos
        for template_id, logo_path in self.template_logos.items():
            template_logo_file = self.config.config_dir / f"logo_{template_id}.png"
            
            import shutil
            shutil.copy2(logo_path, template_logo_file)
        
        QMessageBox.information(
            self, "Success",
            "Configuration and logos updated successfully!"
        )
        
        # Emit signal
        self.setup_complete.emit({
            'student_name': name,
            'student_id': student_id,
            'modules': self.modules,
            'logo_path': self.config.get_logo_path()
        })
        
        self.close()