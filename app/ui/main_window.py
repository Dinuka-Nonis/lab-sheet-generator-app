from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QFileDialog, QApplication, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QAction, QPixmap, QPalette, QColor
from app.core.template_manager import get_template_manager
from app.utils.paths import get_output_dir
import os
from pathlib import Path
from app.scheduler.schedule_manager import ScheduleManager
from app.ui.schedule_window import ScheduleWindow

# OneDrive Integration (V3.0)
try:
    from app.cloud.onedrive_client import OneDriveClient
    from app.cloud.sync_manager import SyncManager
    from app.cloud.azure_config import get_client_id
    ONEDRIVE_AVAILABLE = True
except ImportError:
    ONEDRIVE_AVAILABLE = False


class GeneratorThread(QThread):
    """Thread for generating lab sheets without blocking UI."""
    
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, template, student_name, student_id, module_name, module_code, 
                 sheet_label, logo_path, output_dir):
        super().__init__()
        self.template = template
        self.student_name = student_name
        self.student_id = student_id
        self.module_name = module_name
        self.module_code = module_code
        self.sheet_label = sheet_label
        self.logo_path = logo_path
        self.output_dir = output_dir
    
    def run(self):
        """Generate the lab sheet."""
        try:
            original_dir = os.getcwd()
            os.chdir(self.output_dir)
            
            print(f"GENERATION: Using template: {self.template.__class__.__name__}")
            
            output_file = self.template.generate(
                student_name=self.student_name,
                student_id=self.student_id,
                module_name=self.module_name,
                module_code=self.module_code,
                sheet_label=self.sheet_label,
                logo_path=str(self.logo_path) if self.logo_path else None
            )
            
            os.chdir(original_dir)
            full_path = os.path.join(self.output_dir, output_file)
            self.finished.emit(full_path)
            
        except Exception as e:
            os.chdir(original_dir)
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for generating lab sheets."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.config_data = config.load_config()
        self.global_output_dir = self.config_data.get('global_output_path', str(get_output_dir()))
        self.generator_thread = None
        
        # Initialize OneDrive components (V3.0)
        if ONEDRIVE_AVAILABLE:
            try:
                client_id = get_client_id()
                self.onedrive_client = OneDriveClient(
                    client_id=client_id,
                    config_dir=self.config.config_dir
                )
                self.sync_manager = SyncManager(
                    config=self.config,
                    onedrive_client=self.onedrive_client
                )
                self.onedrive_enabled = True
            except ValueError as e:
                # Client ID not configured yet
                print(f"OneDrive not configured: {e}")
                self.onedrive_client = None
                self.sync_manager = None
                self.onedrive_enabled = False
        else:
            self.onedrive_client = None
            self.sync_manager = None
            self.onedrive_enabled = False
        
        self.setWindowTitle("Lab Sheet Generator V3.0 (OneDrive Beta)")
        self.setMinimumSize(820, 720)
        
        # Set white title bar and window colors
        self.set_white_title_bar()
        
        self.init_ui()
        self.init_menu()
    
    def set_white_title_bar(self):
        """Set the title bar to white for better aesthetics."""
        # Set window background to white
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(26, 26, 26))
        self.setPalette(palette)
    
    def init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()
        
        # Style the menu bar to be white
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: white;
                color: #24292e;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_output_action = QAction("Open Output Folder", self)
        open_output_action.triggered.connect(self.open_output_folder)
        file_menu.addAction(open_output_action)
        
        change_output_action = QAction("Change Default Output Folder", self)
        change_output_action.triggered.connect(self.change_global_output_folder)
        file_menu.addAction(change_output_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        
        edit_config_action = QAction("Edit Configuration", self)
        edit_config_action.triggered.connect(self.edit_configuration)
        settings_menu.addAction(edit_config_action)
        
        reset_config_action = QAction("Reset Configuration", self)
        reset_config_action.triggered.connect(self.reset_configuration)
        settings_menu.addAction(reset_config_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_ui(self):
        """Initialize the user interface with scrollable content."""
        # Create central widget with scroll area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout for central widget
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create content widget for scroll area
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(28, 28, 28, 28)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        header = QLabel("Lab Sheet Generator")
        header.setStyleSheet("""
            font-size: 32px; 
            font-weight: 700; 
            color: #1a1a1a;
            letter-spacing: -0.5px;
        """)
        header.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(header)
        
        subtitle = QLabel("Generate professional lab sheet documents")
        subtitle.setStyleSheet("""
            font-size: 16px; 
            color: #586069;
            font-weight: 400;
        """)
        subtitle.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(subtitle)
        
        main_layout.addLayout(header_layout)
        
        # Student Info Display
        info_group = QGroupBox("Your Information")
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
            }
        """)
        info_layout = QVBoxLayout()
        
        self.student_info_label = QLabel()
        self.student_info_label.setStyleSheet("""
            font-size: 15px; 
            padding: 12px; 
            line-height: 1.6;
        """)
        self.student_info_label.setWordWrap(True)
        self.update_student_info_display()
        info_layout.addWidget(self.student_info_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Logo Status
        logo_group = QGroupBox("University Logo")
        logo_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
            }
        """)
        logo_layout = QHBoxLayout()
        
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(90, 86)
        self.logo_preview.setStyleSheet("""
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            background-color: #f6f8fa;
        """)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        
        # Get logo for current template
        logo_path = self.get_current_template_logo()
        if logo_path and logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            self.logo_status_label = QLabel("✓ Logo loaded")
            self.logo_status_label.setStyleSheet("""
                color: #28a745; 
                font-weight: 600; 
                font-size: 15px;
            """)
        else:
            self.logo_preview.setText("No Logo")
            self.logo_status_label = QLabel("⚠ No logo set")
            self.logo_status_label.setStyleSheet("""
                color: #ffa500; 
                font-weight: 600; 
                font-size: 15px;
            """)
        
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addWidget(self.logo_status_label, 0, Qt.AlignVCenter)
        logo_layout.addStretch()
        
        logo_group.setLayout(logo_layout)
        main_layout.addWidget(logo_group)
        
        # OneDrive Cloud Sync Section (V3.0)
        if hasattr(self, "create_onedrive_section"):
            onedrive_group = self.create_onedrive_section()
            main_layout.addWidget(onedrive_group)
        
        # Generator Section
        generator_group = QGroupBox("Generate Lab Sheet")
        generator_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
            }
        """)
        generator_layout = QFormLayout()
        generator_layout.setSpacing(18)
        generator_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        generator_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Style for form labels
        label_style = "font-size: 15px; font-weight: 500; color: #24292e;"
        
        # Module selection
        self.module_combo = QComboBox()
        self.module_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.module_combo.setMinimumHeight(44)
        self.module_combo.currentIndexChanged.connect(self.on_module_changed)
        
        module_label = QLabel("Select Module:")
        module_label.setStyleSheet(label_style)
        generator_layout.addRow(module_label, self.module_combo)
        
        # Sheet type display
        self.sheet_type_label = QLabel("Practical")
        self.sheet_type_label.setStyleSheet("""
            font-weight: 600; 
            font-size: 15px; 
            color: #24292e;
        """)
        
        type_label = QLabel("Sheet Type:")
        type_label.setStyleSheet(label_style)
        generator_layout.addRow(type_label, self.sheet_type_label)
        
        # Template display and change button
        template_layout = QHBoxLayout()
        template_layout.setSpacing(12)
        
        self.template_label = QLabel("Template: Classic")
        self.template_label.setStyleSheet("""
            font-weight: 600; 
            font-size: 15px; 
            color: #5b8def;
        """)
        self.template_label.setWordWrap(True)
        template_layout.addWidget(self.template_label, 1)
        
        self.change_template_btn = QPushButton("Change Template")
        self.change_template_btn.setProperty("styleClass", "secondary")
        self.change_template_btn.setMinimumWidth(160)
        self.change_template_btn.setMinimumHeight(42)
        self.change_template_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
            }
        """)
        self.change_template_btn.clicked.connect(self.change_template)
        self.change_template_btn.setEnabled(False)
        template_layout.addWidget(self.change_template_btn)
        
        template_widget = QWidget()
        template_widget.setLayout(template_layout)
        
        template_label_widget = QLabel("Document Template:")
        template_label_widget.setStyleSheet(label_style)
        generator_layout.addRow(template_label_widget, template_widget)
        
        # Sheet number
        self.sheet_spin = QSpinBox()
        self.sheet_spin.setMinimumHeight(44)
        self.sheet_spin.setMinimum(1)
        self.sheet_spin.setMaximum(99)
        self.sheet_spin.setValue(1)
        self.sheet_spin.valueChanged.connect(self.update_filename_preview)
        
        sheet_num_label = QLabel("Sheet Number:")
        sheet_num_label.setStyleSheet(label_style)
        generator_layout.addRow(sheet_num_label, self.sheet_spin)
        
        # Output path with browse button
        output_layout = QHBoxLayout()
        output_layout.setSpacing(12)
        
        self.output_path_label = QLabel()
        self.output_path_label.setStyleSheet("font-size: 14px; color: #586069;")
        self.output_path_label.setWordWrap(True)
        self.output_path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        output_layout.addWidget(self.output_path_label, 1)
        
        browse_output_btn = QPushButton("Browse...")
        browse_output_btn.setProperty("styleClass", "secondary")
        browse_output_btn.setMinimumWidth(110)
        browse_output_btn.setMinimumHeight(42)
        browse_output_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
            }
        """)
        browse_output_btn.clicked.connect(self.browse_module_output_path)
        output_layout.addWidget(browse_output_btn)
        
        output_widget = QWidget()
        output_widget.setLayout(output_layout)
        
        output_label_widget = QLabel("Output Path:")
        output_label_widget.setStyleSheet(label_style)
        generator_layout.addRow(output_label_widget, output_widget)
        
        # Filename preview
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet("""
            padding: 14px 18px;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            background-color: #f6f8fa;
            color: #24292e;
            font-weight: 500;
        """)
        self.filename_preview.setWordWrap(True)
        self.filename_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        preview_label_widget = QLabel("File Preview:")
        preview_label_widget.setStyleSheet(label_style)
        generator_layout.addRow(preview_label_widget, self.filename_preview)
        
        generator_group.setLayout(generator_layout)
        main_layout.addWidget(generator_group)
        
        # Generate button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Lab Sheet")
        self.generate_btn.setMinimumWidth(220)
        self.generate_btn.setMinimumHeight(52)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_lab_sheet)
        button_layout.addWidget(self.generate_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 15px; padding: 16px; font-weight: 500;")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        # Set content widget layout
        content_widget.setLayout(main_layout)
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to central layout
        central_layout.addWidget(scroll_area)
        central_widget.setLayout(central_layout)
        
        # Populate modules
        self.populate_modules()
    
    def get_current_template_logo(self):
        """Get logo for currently selected template."""
        if not self.config_data or not self.config_data.get('modules'):
            return self.config.get_logo_path()
        
        # Get first module's template (or we could track current module)
        first_module = self.config_data['modules'][0]
        template_id = first_module.get('template', 'classic')
        
        # Check for template-specific logo
        template_logo_path = self.config.config_dir / f"logo_{template_id}.png"
        if template_logo_path.exists():
            return template_logo_path
        
        # Fall back to default logo
        return self.config.get_logo_path()
    
    def update_student_info_display(self):
        """Update the student information display."""
        name = self.config_data.get('student_name', 'Not set')
        student_id = self.config_data.get('student_id', 'Not set')
        user_email = self.config_data.get('user_email', 'Not set')
        
        # Count modules
        modules = self.config_data.get('modules', [])
        module_count = len(modules)
        
        info_text = f"""
        <div style='line-height: 1.8;'>
            <p style='margin: 4px 0;'><b>Name:</b> {name}</p>
            <p style='margin: 4px 0;'><b>Student ID:</b> {student_id}</p>
            <p style='margin: 4px 0;'><b>Email:</b> {user_email}</p>
            <p style='margin: 4px 0;'><b>Modules:</b> {module_count} configured</p>
        </div>
        """
        
        self.student_info_label.setText(info_text)
    
    def populate_modules(self):
        """Populate the module combo box."""
        self.module_combo.clear()
        
        if not self.config_data or not self.config_data.get('modules'):
            self.module_combo.addItem("No modules configured", None)
            self.generate_btn.setEnabled(False)
            return
        
        for module in self.config_data['modules']:
            display_text = f"{module['name']} ({module['code']})"
            self.module_combo.addItem(display_text, module)
        
        self.generate_btn.setEnabled(True)
        
        if self.module_combo.count() > 0:
            self.on_module_changed()
    
    def on_module_changed(self):
        """Handle module selection change."""
        module = self.module_combo.currentData()
        if not module:
            return
        
        # Update sheet type
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        self.sheet_type_label.setText(sheet_type)
        
        # Update template display
        template_id = module.get('template', 'classic')
        try:
            manager = get_template_manager()
            template = manager.get_template(template_id)
            self.template_label.setText(f"Template: {template.template_name}")
        except KeyError:
            self.template_label.setText(f"Template: {template_id.title()}")
        
        # Update logo for this template
        self.update_logo_for_template(template_id)
        
        self.change_template_btn.setEnabled(True)
        self.update_output_path_display()
        self.update_filename_preview()
    
    def update_logo_for_template(self, template_id):
        """Update logo display based on template."""
        # Check for template-specific logo
        template_logo_path = self.config.config_dir / f"logo_{template_id}.png"
        
        if template_logo_path.exists():
            logo_path = template_logo_path
        else:
            logo_path = self.config.get_logo_path()
        
        if logo_path and logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            self.logo_status_label.setText("✓ Logo loaded")
            self.logo_status_label.setStyleSheet("""
                color: #28a745; 
                font-weight: 600; 
                font-size: 15px;
            """)
        else:
            self.logo_preview.setText("No Logo")
            self.logo_preview.setPixmap(QPixmap())
            self.logo_status_label.setText("⚠ No logo for this template")
            self.logo_status_label.setStyleSheet("""
                color: #ffa500; 
                font-weight: 600; 
                font-size: 15px;
            """)
    
    def change_template(self):
        """Change template for current module."""
        from app.ui.template_selector import show_template_selector
        
        module = self.module_combo.currentData()
        if not module:
            return
        
        current_template = module.get('template', 'classic')
        selected = show_template_selector(current_template, self)
        
        if selected and selected != current_template:
            # Update module
            module_index = self.module_combo.currentIndex()
            self.config_data['modules'][module_index]['template'] = selected
            module['template'] = selected
            
            # Update display
            try:
                manager = get_template_manager()
                template = manager.get_template(selected)
                self.template_label.setText(f"Template: {template.template_name}")
            except KeyError:
                self.template_label.setText(f"Template: {selected.title()}")
            
            # Update logo for new template
            self.update_logo_for_template(selected)
            
            # Save config
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                self.config_data['global_output_path'],
                'light',
                self.config_data.get('default_template', 'classic')
            )
    
    def update_output_path_display(self):
        """Update the output path display."""
        module = self.module_combo.currentData()
        if module:
            output_dir = module.get('output_path') or self.global_output_dir
            self.output_path_label.setText(output_dir)
    
    def browse_module_output_path(self):
        """Browse for module-specific output path."""
        module = self.module_combo.currentData()
        if not module:
            return
        
        current_path = module.get('output_path') or self.global_output_dir
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder for This Module",
            current_path
        )
        
        if folder:
            module['output_path'] = folder
            self.output_path_label.setText(folder)
            
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                self.config_data['global_output_path'],
                'light',
                self.config_data.get('default_template', 'classic')
            )
    
    def update_filename_preview(self):
        """Update the filename preview."""
        module = self.module_combo.currentData()
        if not module or not self.config_data:
            return
        
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        sheet_num = self.sheet_spin.value()
        use_padding = module.get('use_zero_padding', True)
        
        if use_padding:
            sheet_label = f"{sheet_type} {sheet_num:02d}"
        else:
            sheet_label = f"{sheet_type} {sheet_num}"
        
        student_id = self.config_data['student_id']
        filename = f"{sheet_label.replace(' ', '_')}_{student_id}.docx"
        
        self.filename_preview.setText(f"📄  {filename}")
    
    def generate_lab_sheet(self):
        """Generate lab sheet using selected template."""
        module = self.module_combo.currentData()
        if not module:
            QMessageBox.warning(self, "No Module", "Please select a module.")
            return
        
        # Get template from module
        manager = get_template_manager()
        template_id = module.get('template', 'classic')
        
        try:
            template = manager.get_template(template_id)
        except KeyError as e:
            QMessageBox.critical(
                self, "Error",
                f"Template '{template_id}' not found!\n\nUsing Classic template."
            )
            template = manager.get_template('classic')
        
        # Build sheet label
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        sheet_num = self.sheet_spin.value()
        use_padding = module.get('use_zero_padding', True)
        
        if use_padding:
            sheet_label = f"{sheet_type} {sheet_num:02d}"
        else:
            sheet_label = f"{sheet_type} {sheet_num}"
        
        output_dir = module.get('output_path') or self.global_output_dir
        
        # Get template-specific logo
        template_logo_path = self.config.config_dir / f"logo_{template_id}.png"
        if template_logo_path.exists():
            logo_path = template_logo_path
        else:
            logo_path = self.config.get_logo_path()
        
        if not logo_path or not logo_path.exists():
            reply = QMessageBox.question(
                self,
                "No Logo",
                f"No logo configured for '{template_id}' template. Generate without logo?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            logo_path = None
        
        self.generate_btn.setEnabled(False)
        self.status_label.setText("⏳ Generating lab sheet...")
        self.status_label.setStyleSheet("font-size: 15px; padding: 16px; color: #5b8def; font-weight: 600;")
        
        self.generator_thread = GeneratorThread(
            template=template,
            student_name=self.config_data['student_name'],
            student_id=self.config_data['student_id'],
            module_name=module['name'],
            module_code=module['code'],
            sheet_label=sheet_label,
            logo_path=logo_path,
            output_dir=output_dir
        )
        
        self.generator_thread.finished.connect(self.on_generation_complete)
        self.generator_thread.error.connect(self.on_generation_error)
        self.generator_thread.start()
    
    def on_generation_complete(self, file_path):
        """Called when generation is complete."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText("✓ Lab sheet generated successfully!")
        self.status_label.setStyleSheet("color: #28a745; font-weight: 600; font-size: 15px; padding: 16px;")
        
        reply = QMessageBox.information(
            self,
            "Success",
            f"Lab sheet generated successfully!\n\nSaved to:\n{file_path}\n\nWould you like to open the folder?",
            QMessageBox.Open | QMessageBox.Close
        )
        
        if reply == QMessageBox.Open:
            folder_path = os.path.dirname(file_path)
            self.open_folder(folder_path)
    
    def on_generation_error(self, error_msg):
        """Called when generation fails."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText("✗ Generation failed")
        self.status_label.setStyleSheet("color: #d73a49; font-weight: 600; font-size: 15px; padding: 16px;")
        
        QMessageBox.critical(
            self,
            "Error",
            f"Failed to generate lab sheet:\n\n{error_msg}"
        )
    
    def open_output_folder(self):
        """Open the current module's output folder."""
        module = self.module_combo.currentData()
        if module:
            output_dir = module.get('output_path') or self.global_output_dir
        else:
            output_dir = self.global_output_dir
        
        self.open_folder(output_dir)
    
    def open_folder(self, folder_path):
        """Open a folder in the file explorer."""
        if os.name == 'nt':
            os.startfile(folder_path)
        elif os.name == 'posix':
            import subprocess
            if os.uname().sysname == 'Darwin':
                subprocess.run(['open', folder_path])
            else:
                subprocess.run(['xdg-open', folder_path])
    
    def change_global_output_folder(self):
        """Change the default global output folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Default Output Folder",
            self.global_output_dir
        )
        
        if folder:
            self.global_output_dir = folder
            self.config_data['global_output_path'] = folder
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                folder,
                'light',
                self.config_data.get('default_template', 'classic')
            )
            
            self.update_output_path_display()
            
            QMessageBox.information(
                self,
                "Output Folder Changed",
                f"Default output folder changed to:\n{folder}"
            )
    
    def edit_configuration(self):
        """Open setup wizard to edit configuration."""
        from app.ui.setup_window import SetupWindow
        
        try:
            # FIXED: Don't pass is_first_run parameter
            setup_window = SetupWindow(self.config, self)
            setup_window.load_existing_config()  # ADD THIS LINE

            
            # Load current data
            setup_window.name_input.setText(self.config_data.get('student_name', ''))
            setup_window.id_input.setText(self.config_data.get('student_id', ''))
            
            # Load modules with all required fields
            modules = []
            for module in self.config_data.get('modules', []):
                complete_module = {
                    'name': module.get('name', ''),
                    'code': module.get('code', ''),
                    'sheet_type': module.get('sheet_type', 'Practical'),
                    'custom_sheet_type': module.get('custom_sheet_type'),
                    'output_path': module.get('output_path'),
                    'use_zero_padding': module.get('use_zero_padding', True),
                    'template': module.get('template', 'classic')
                }
                modules.append(complete_module)
            
            setup_window.modules = modules
            setup_window.update_module_list()
            
            # Load logos for all templates
            setup_window.load_logos_from_config(self.config)
            
            # Connect callback
            def on_complete(config_data):
                self.config_data = self.config.load_config()
                self.global_output_dir = self.config_data.get('global_output_path', str(get_output_dir()))
                self.update_student_info_display()
                self.populate_modules()
                
                # Update logo for current template
                if self.config_data and self.config_data.get('modules'):
                    first_module = self.config_data['modules'][0]
                    template_id = first_module.get('template', 'classic')
                    self.update_logo_for_template(template_id)
            
            setup_window.setup_complete.connect(on_complete)
            setup_window.show()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to open editor:\n\n{str(e)}")
    
    def reset_configuration(self):
        """Reset all configuration."""
        reply = QMessageBox.warning(
            self,
            "Reset Configuration",
            "Are you sure you want to reset all configuration?\n\nThis will delete your student info, modules, and logos.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.reset_config()
            QMessageBox.information(
                self,
                "Configuration Reset",
                "Configuration has been reset. Please restart the application."
            )
            self.close()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Lab Sheet Generator",
            "<h3 style='font-weight: 700;'>Lab Sheet Generator V3.0 (OneDrive Beta).0</h3>"
            "<p style='font-size: 14px;'>A modern desktop application for university students to generate "
            "lab sheet templates automatically.</p>"
            "<p style='font-size: 14px;'><b>Features:</b></p>"
            "<ul style='font-size: 14px;'>"
            "<li> Clean, modern UI design</li>"
            "<li> Multiple document templates</li>"
            "<li> Template-specific logos</li>"
            "<li> Enhanced user experience</li>"
            "</ul>"
        )    
    # ==========================================
    # OneDrive Integration Methods (V3.0)
    # ==========================================
    
    def create_onedrive_section(self):
        """Create OneDrive cloud sync section."""
        onedrive_group = QGroupBox("☁️ Cloud Sync (OneDrive)")
        onedrive_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                padding-top: 16px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        
        onedrive_layout = QVBoxLayout()
        onedrive_layout.setSpacing(12)
        
        if not self.onedrive_enabled:
            # Show setup required message
            info_label = QLabel(
                "⚠️ OneDrive integration requires Azure configuration.\n"
                "Please see AZURE_SETUP_GUIDE.md for setup instructions."
            )
            info_label.setStyleSheet("""
                color: #ffa500;
                font-size: 14px;
                padding: 12px;
                background-color: #fffbf0;
                border-radius: 6px;
                border: 1px solid #ffe59e;
            """)
            info_label.setWordWrap(True)
            onedrive_layout.addWidget(info_label)
            
            setup_btn = QPushButton("📖 Open Setup Guide")
            setup_btn.setMinimumHeight(44)
            setup_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffa500;
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    padding: 12px;
                }
                QPushButton:hover {
                    background-color: #ff8c00;
                }
            """)
            setup_btn.clicked.connect(self.open_setup_guide)
            onedrive_layout.addWidget(setup_btn)
        else:
            # Connection status row
            status_layout = QHBoxLayout()
            status_layout.setSpacing(12)
            
            self.onedrive_status_label = QLabel("● Not connected")
            self.onedrive_status_label.setStyleSheet("""
                font-size: 15px;
                font-weight: 600;
                color: #6a737d;
            """)
            status_layout.addWidget(self.onedrive_status_label)
            status_layout.addStretch()
            
            # Connect/Disconnect button
            self.onedrive_connect_btn = QPushButton("Connect OneDrive")
            self.onedrive_connect_btn.setMinimumHeight(44)
            self.onedrive_connect_btn.setMinimumWidth(180)
            self.onedrive_connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """)
            self.onedrive_connect_btn.clicked.connect(self.handle_onedrive_connection)
            status_layout.addWidget(self.onedrive_connect_btn)
            
            onedrive_layout.addLayout(status_layout)
            
            # User info (hidden initially)
            self.onedrive_user_info = QLabel()
            self.onedrive_user_info.setStyleSheet("""
                font-size: 14px;
                color: #586069;
                padding: 8px;
                background-color: #f6f8fa;
                border-radius: 4px;
            """)
            self.onedrive_user_info.setWordWrap(True)
            self.onedrive_user_info.setVisible(False)
            onedrive_layout.addWidget(self.onedrive_user_info)
            
            # Sync button (hidden initially)
            self.sync_now_btn = QPushButton("🔄 Sync Configuration Now")
            self.sync_now_btn.setMinimumHeight(42)
            self.sync_now_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    font-size: 14px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:disabled {
                    background-color: #94d3a2;
                }
            """)
            self.sync_now_btn.clicked.connect(self.manual_sync_to_cloud)
            self.sync_now_btn.setVisible(False)
            onedrive_layout.addWidget(self.sync_now_btn)
            
            # Last sync info (hidden initially)
            self.last_sync_label = QLabel()
            self.last_sync_label.setStyleSheet("""
                font-size: 13px;
                color: #6a737d;
                padding: 4px;
            """)
            self.last_sync_label.setVisible(False)
            onedrive_layout.addWidget(self.last_sync_label)
            
            # Check if already authenticated
            if self.onedrive_client and self.onedrive_client.authenticate_silent():
                self.update_onedrive_ui_connected()
        
        onedrive_group.setLayout(onedrive_layout)
        return onedrive_group
    
    def handle_onedrive_connection(self):
        """Handle OneDrive connection button click."""
        if not self.onedrive_enabled:
            QMessageBox.information(
                self,
                "Setup Required",
                "Please complete Azure configuration first.\n"
                "See AZURE_SETUP_GUIDE.md for instructions."
            )
            return
        
        if self.onedrive_client.is_authenticated():
            # Already connected - offer to disconnect
            reply = QMessageBox.question(
                self,
                "Disconnect OneDrive",
                "Are you sure you want to disconnect from OneDrive?\n\n"
                "Your files will remain in OneDrive, but automatic sync will be disabled.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.onedrive_client.logout()
                self.update_onedrive_ui_disconnected()
                
                QMessageBox.information(
                    self,
                    "Disconnected",
                    "OneDrive has been disconnected."
                )
        else:
            # Not connected - authenticate
            self.status_label.setText("Connecting to OneDrive...")
            self.status_label.setStyleSheet("color: #0078d4; font-weight: 600; font-size: 15px; padding: 16px;")
            
            # Process events to update UI
            QApplication.processEvents()
            
            # Authenticate (this will open browser)
            success = self.onedrive_client.authenticate_interactive()
            
            if success:
                self.update_onedrive_ui_connected()
                
                # Ensure folder structure
                self.onedrive_client.ensure_folder_structure()
                
                # Initial sync to cloud
                self.sync_manager.sync_to_cloud()
                
                # Sync logo if exists
                logo_path = self.config.get_logo_path()
                if logo_path:
                    self.sync_manager.sync_logo(logo_path)
                
                self.status_label.setText("✓ OneDrive connected successfully!")
                self.status_label.setStyleSheet("color: #28a745; font-weight: 600; font-size: 15px; padding: 16px;")
                
                QMessageBox.information(
                    self,
                    "Connected Successfully",
                    "OneDrive connected successfully!\n\n"
                    "Your configuration has been synced to the cloud.\n"
                    "Lab sheets will now be automatically uploaded to OneDrive."
                )
            else:
                self.status_label.setText("✗ Connection failed")
                self.status_label.setStyleSheet("color: #d73a49; font-weight: 600; font-size: 15px; padding: 16px;")
                
                QMessageBox.warning(
                    self,
                    "Connection Failed",
                    "Failed to connect to OneDrive.\n\n"
                    "Please check:\n"
                    "• Internet connection\n"
                    "• Azure configuration\n"
                    "• Microsoft account access"
                )
    
    def update_onedrive_ui_connected(self):
        """Update UI to show connected state."""
        # Get user info
        user_info = self.onedrive_client.get_user_info()
        
        if user_info:
            display_name = user_info.get('displayName', 'User')
            email = user_info.get('userPrincipalName', '')
            
            self.onedrive_status_label.setText(f"● Connected")
            self.onedrive_status_label.setStyleSheet("""
                font-size: 15px;
                font-weight: 600;
                color: #28a745;
            """)
            
            # Show both accounts clearly
            user_email = self.config_data.get('user_email', 'Not configured')
            self.onedrive_user_info.setText(
                f"🔐 Storage: {email}\n"
                f"📧 Notifications: {user_email}"
            )            
            self.onedrive_user_info.setVisible(True)
            
            self.onedrive_connect_btn.setText("Disconnect")
            self.onedrive_connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6a737d;
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                    padding: 12px 24px;
                }
                QPushButton:hover {
                    background-color: #586069;
                }
            """)
            
            self.sync_now_btn.setVisible(True)
            
            # Show last sync info
            sync_info = self.sync_manager.get_last_sync_info()
            if sync_info:
                from datetime import datetime
                sync_time = datetime.fromisoformat(sync_info['last_sync_time'])
                time_str = sync_time.strftime('%B %d, %Y at %I:%M %p')
                self.last_sync_label.setText(f"Last synced: {time_str}")
                self.last_sync_label.setVisible(True)
    
    def update_onedrive_ui_disconnected(self):
        """Update UI to show disconnected state."""
        self.onedrive_status_label.setText("● Not connected")
        self.onedrive_status_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #6a737d;
        """)
        
        self.onedrive_user_info.setVisible(False)
        
        self.onedrive_connect_btn.setText("Connect OneDrive")
        self.onedrive_connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        
        self.sync_now_btn.setVisible(False)
        self.last_sync_label.setVisible(False)
    
    def manual_sync_to_cloud(self):
        """Manually sync configuration to OneDrive."""
        if not self.onedrive_client.is_authenticated():
            QMessageBox.warning(
                self,
                "Not Connected",
                "Please connect to OneDrive first."
            )
            return
        
        self.sync_now_btn.setEnabled(False)
        self.sync_now_btn.setText("Syncing...")
        QApplication.processEvents()
        
        # Sync config
        config_success = self.sync_manager.sync_to_cloud()
        
        # Try to sync logo from multiple locations
        logo_synced = False
        
        # 1. Try default logo location
        logo_path = self.config.get_logo_path()
        if logo_path and logo_path.exists():
            print(f"Found logo at: {logo_path}")
            logo_synced = self.sync_manager.sync_logo(logo_path)
        
        # 2. Try template-specific logo
        if not logo_synced:
            for template_id in ['classic', 'sliit']:
                template_logo = self.config.config_dir / f"logo_{template_id}.png"
                if template_logo.exists():
                    print(f"Found template logo at: {template_logo}")
                    logo_synced = self.sync_manager.sync_logo(template_logo)
                    break
        
        # 3. Try any PNG in config dir
        if not logo_synced:
            for png_file in self.config.config_dir.glob("*.png"):
                print(f"Found PNG at: {png_file}")
                logo_synced = self.sync_manager.sync_logo(png_file)
                break
        
        self.sync_now_btn.setEnabled(True)
        self.sync_now_btn.setText("🔄 Sync Configuration Now")
        
        if config_success:
            # Build status message
            status_parts = ["✓ Configuration synced!"]
            if logo_synced:
                status_parts.append("✓ Logo synced!")
            else:
                status_parts.append("⚠ No logo found")
            
            # Update last sync info
            sync_info = self.sync_manager.get_last_sync_info()
            if sync_info:
                from datetime import datetime
                sync_time = datetime.fromisoformat(sync_info['last_sync_time'])
                time_str = sync_time.strftime('%B %d, %Y at %I:%M %p')
                self.last_sync_label.setText(f"Last synced: {time_str}")
                self.last_sync_label.setVisible(True)
            
            self.status_label.setText(" | ".join(status_parts))
            self.status_label.setStyleSheet("color: #28a745; font-weight: 600; font-size: 15px; padding: 16px;")
        else:
            self.status_label.setText("✗ Sync failed - check internet connection")
            self.status_label.setStyleSheet("color: #d73a49; font-weight: 600; font-size: 15px; padding: 16px;")

    def open_setup_guide(self):
        """Open Azure setup guide."""
        import webbrowser
        
        guide_path = Path(__file__).parent.parent.parent / "AZURE_SETUP_GUIDE.md"
        
        if guide_path.exists():
            # Try to open with default markdown viewer
            if os.name == 'nt':  # Windows
                os.startfile(str(guide_path))
            elif os.name == 'posix':  # macOS/Linux
                import subprocess
                if os.uname().sysname == 'Darwin':
                    subprocess.run(['open', str(guide_path)])
                else:
                    subprocess.run(['xdg-open', str(guide_path)])
        else:
            QMessageBox.information(
                self,
                "Setup Guide",
                "Please see AZURE_SETUP_GUIDE.md in the project root folder."
            )
