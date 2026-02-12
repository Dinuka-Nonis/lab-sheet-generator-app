"""
Main Window for Lab Sheet Generator V3.0
Clean, refactored version with separated concerns
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QFileDialog, QApplication, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QPixmap, QPalette, QColor
from app.core.template_manager import get_template_manager
from app.utils.paths import get_output_dir
import os
from pathlib import Path

# Phase 2: Schedule Management
from app.scheduler.schedule_manager import ScheduleManager
from app.ui.schedule_window import ScheduleWindow

# OneDrive Integration
from app.ui.onedrive_widget import OneDriveWidget, OneDriveSetupWidget

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
        
        # Initialize OneDrive
        self.setup_onedrive()
        
        # Initialize Schedule Manager
        self.schedule_manager = ScheduleManager(
            config=self.config,
            onedrive_client=self.onedrive_client if self.onedrive_enabled else None
        )
        
        self.setWindowTitle("Lab Sheet Generator V3.0")
        self.setMinimumSize(820, 720)
        self.set_white_theme()
        
        self.init_menu()
        self.init_ui()
    
    def setup_onedrive(self):
        """Setup OneDrive components."""
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
            except ValueError:
                self.onedrive_client = None
                self.sync_manager = None
                self.onedrive_enabled = False
        else:
            self.onedrive_client = None
            self.sync_manager = None
            self.onedrive_enabled = False
    
    def set_white_theme(self):
        """Set white color scheme."""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(26, 26, 26))
        self.setPalette(palette)
    
    def init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()
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
        file_menu.addAction(self.create_action("Open Output Folder", self.open_output_folder))
        file_menu.addAction(self.create_action("Change Default Output Folder", self.change_global_output_folder))
        file_menu.addSeparator()
        file_menu.addAction(self.create_action("Exit", self.close))
        
        # Settings menu
        settings_menu = menubar.addMenu("Settings")
        settings_menu.addAction(self.create_action("Edit Configuration", self.edit_configuration))
        settings_menu.addAction(self.create_action("Manage Schedules", self.open_schedule_manager))
        settings_menu.addAction(self.create_action("Reset Configuration", self.reset_configuration))
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction(self.create_action("About", self.show_about))
    
    def create_action(self, text, slot):
        """Helper to create menu actions."""
        action = QAction(text, self)
        action.triggered.connect(slot)
        return action
    
    def init_ui(self):
        """Initialize the user interface."""
        # Create scrollable central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(28, 28, 28, 28)
        
        # Add sections
        main_layout.addWidget(self.create_header())
        main_layout.addWidget(self.create_info_section())
        main_layout.addWidget(self.create_logo_section())
        
        # OneDrive section
        if self.onedrive_enabled:
            main_layout.addWidget(self.create_onedrive_section())
        
        main_layout.addWidget(self.create_generator_section())
        main_layout.addLayout(self.create_button_section())
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 15px; padding: 16px; font-weight: 500;")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        content_widget.setLayout(main_layout)
        scroll_area.setWidget(content_widget)
        central_layout.addWidget(scroll_area)
        central_widget.setLayout(central_layout)
        
        # Populate modules
        self.populate_modules()
    
    def create_header(self):
        """Create header section."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        title = QLabel("Lab Sheet Generator")
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #1a1a1a;")
        title.setAlignment(Qt.AlignLeft)
        
        subtitle = QLabel("Generate professional lab sheet documents")
        subtitle.setStyleSheet("font-size: 16px; color: #586069;")
        subtitle.setAlignment(Qt.AlignLeft)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        widget.setLayout(layout)
        return widget
    
    def create_info_section(self):
        """Create student info section."""
        group = QGroupBox("Your Information")
        group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: 600; }")
        
        layout = QVBoxLayout()
        self.student_info_label = QLabel()
        self.student_info_label.setStyleSheet("font-size: 15px; padding: 12px;")
        self.student_info_label.setWordWrap(True)
        self.update_student_info_display()
        
        layout.addWidget(self.student_info_label)
        group.setLayout(layout)
        return group
    
    def create_logo_section(self):
        """Create logo preview section."""
        group = QGroupBox("University Logo")
        group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: 600; }")
        
        layout = QHBoxLayout()
        
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(90, 86)
        self.logo_preview.setStyleSheet("""
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            background-color: #f6f8fa;
        """)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        
        logo_path = self.get_current_template_logo()
        if logo_path and logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self.logo_preview.setPixmap(pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_status_label = QLabel("✓ Logo loaded")
            self.logo_status_label.setStyleSheet("color: #28a745; font-weight: 600; font-size: 15px;")
        else:
            self.logo_preview.setText("No Logo")
            self.logo_status_label = QLabel("⚠ No logo set")
            self.logo_status_label.setStyleSheet("color: #ffa500; font-weight: 600; font-size: 15px;")
        
        layout.addWidget(self.logo_preview)
        layout.addWidget(self.logo_status_label, 0, Qt.AlignVCenter)
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def create_onedrive_section(self):
        """Create OneDrive section."""
        group = QGroupBox("☁️ Cloud Sync (OneDrive)")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                padding-top: 16px;
                margin-top: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        
        if self.onedrive_enabled:
            self.onedrive_widget = OneDriveWidget(
                self.onedrive_client,
                self.sync_manager,
                self.config,
                self
            )
            self.onedrive_widget.connection_changed.connect(self.on_onedrive_connection_changed)
            layout.addWidget(self.onedrive_widget)
        else:
            layout.addWidget(OneDriveSetupWidget(self))
        
        group.setLayout(layout)
        return group
    
    def create_generator_section(self):
        """Create generator controls section."""
        group = QGroupBox("Generate Lab Sheet")
        group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: 600; }")
        
        layout = QFormLayout()
        layout.setSpacing(18)
        label_style = "font-size: 15px; font-weight: 500; color: #24292e;"
        
        # Module selection
        self.module_combo = QComboBox()
        self.module_combo.setMinimumHeight(44)
        self.module_combo.currentIndexChanged.connect(self.on_module_changed)
        layout.addRow(self.create_label("Select Module:", label_style), self.module_combo)
        
        # Sheet type
        self.sheet_type_label = QLabel("Practical")
        self.sheet_type_label.setStyleSheet("font-weight: 600; font-size: 15px;")
        layout.addRow(self.create_label("Sheet Type:", label_style), self.sheet_type_label)
        
        # Template with change button
        template_layout = QHBoxLayout()
        self.template_label = QLabel("Template: Classic")
        self.template_label.setStyleSheet("font-weight: 600; font-size: 15px; color: #5b8def;")
        template_layout.addWidget(self.template_label, 1)
        
        self.change_template_btn = QPushButton("Change Template")
        self.change_template_btn.setMinimumHeight(42)
        self.change_template_btn.clicked.connect(self.change_template)
        self.change_template_btn.setEnabled(False)
        template_layout.addWidget(self.change_template_btn)
        
        template_widget = QWidget()
        template_widget.setLayout(template_layout)
        layout.addRow(self.create_label("Document Template:", label_style), template_widget)
        
        # Sheet number
        self.sheet_spin = QSpinBox()
        self.sheet_spin.setMinimumHeight(44)
        self.sheet_spin.setMinimum(1)
        self.sheet_spin.setMaximum(99)
        self.sheet_spin.setValue(1)
        self.sheet_spin.valueChanged.connect(self.update_filename_preview)
        layout.addRow(self.create_label("Sheet Number:", label_style), self.sheet_spin)
        
        # Output path
        output_layout = QHBoxLayout()
        self.output_path_label = QLabel()
        self.output_path_label.setStyleSheet("font-size: 14px; color: #586069;")
        self.output_path_label.setWordWrap(True)
        output_layout.addWidget(self.output_path_label, 1)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.setMinimumHeight(42)
        browse_btn.clicked.connect(self.browse_module_output_path)
        output_layout.addWidget(browse_btn)
        
        output_widget = QWidget()
        output_widget.setLayout(output_layout)
        layout.addRow(self.create_label("Output Path:", label_style), output_widget)
        
        # Filename preview
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet("""
            padding: 14px 18px;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            background-color: #f6f8fa;
        """)
        self.filename_preview.setWordWrap(True)
        layout.addRow(self.create_label("File Preview:", label_style), self.filename_preview)
        
        group.setLayout(layout)
        return group
    
    def create_button_section(self):
        """Create generate button section."""
        layout = QHBoxLayout()
        layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Lab Sheet")
        self.generate_btn.setMinimumWidth(220)
        self.generate_btn.setMinimumHeight(52)
        self.generate_btn.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.generate_btn.clicked.connect(self.generate_lab_sheet)
        
        layout.addWidget(self.generate_btn)
        layout.addStretch()
        
        return layout
    
    def create_label(self, text, style):
        """Helper to create styled labels."""
        label = QLabel(text)
        label.setStyleSheet(style)
        return label
    
    # ==========================================
    # Data and State Management
    # ==========================================
    
    def get_current_template_logo(self):
        """Get logo for currently selected template."""
        if not self.config_data or not self.config_data.get('modules'):
            return self.config.get_logo_path()
        
        first_module = self.config_data['modules'][0]
        template_id = first_module.get('template', 'classic')
        template_logo_path = self.config.config_dir / f"logo_{template_id}.png"
        
        return template_logo_path if template_logo_path.exists() else self.config.get_logo_path()
    
    def update_student_info_display(self):
        """Update student information display."""
        name = self.config_data.get('student_name', 'Not set')
        student_id = self.config_data.get('student_id', 'Not set')
        user_email = self.config_data.get('user_email', 'Not set')
        modules = self.config_data.get('modules', [])
        active_schedules = len(self.schedule_manager.get_active_schedules())
        
        self.student_info_label.setText(f"""
            <div style='line-height: 1.8;'>
                <p style='margin: 4px 0;'><b>Name:</b> {name}</p>
                <p style='margin: 4px 0;'><b>Student ID:</b> {student_id}</p>
                <p style='margin: 4px 0;'><b>Email:</b> {user_email}</p>
                <p style='margin: 4px 0;'><b>Modules:</b> {len(modules)} configured</p>
                <p style='margin: 4px 0;'><b>Schedules:</b> {active_schedules} active</p>
            </div>
        """)
    
    def populate_modules(self):
        """Populate module dropdown."""
        self.module_combo.clear()
        
        if not self.config_data or not self.config_data.get('modules'):
            self.module_combo.addItem("No modules configured", None)
            self.generate_btn.setEnabled(False)
            return
        
        for module in self.config_data['modules']:
            self.module_combo.addItem(f"{module['name']} ({module['code']})", module)
        
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
        
        # Update template
        template_id = module.get('template', 'classic')
        try:
            manager = get_template_manager()
            template = manager.get_template(template_id)
            self.template_label.setText(f"Template: {template.template_name}")
        except KeyError:
            self.template_label.setText(f"Template: {template_id.title()}")
        
        self.update_logo_for_template(template_id)
        self.change_template_btn.setEnabled(True)
        self.update_output_path_display()
        self.update_filename_preview()
    
    def update_logo_for_template(self, template_id):
        """Update logo display for template."""
        template_logo_path = self.config.config_dir / f"logo_{template_id}.png"
        logo_path = template_logo_path if template_logo_path.exists() else self.config.get_logo_path()
        
        if logo_path and logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            self.logo_preview.setPixmap(pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_status_label.setText("✓ Logo loaded")
            self.logo_status_label.setStyleSheet("color: #28a745; font-weight: 600; font-size: 15px;")
        else:
            self.logo_preview.setText("No Logo")
            self.logo_preview.setPixmap(QPixmap())
            self.logo_status_label.setText("⚠ No logo for this template")
            self.logo_status_label.setStyleSheet("color: #ffa500; font-weight: 600; font-size: 15px;")
    
    def update_output_path_display(self):
        """Update output path display."""
        module = self.module_combo.currentData()
        if module:
            self.output_path_label.setText(module.get('output_path') or self.global_output_dir)
    
    def update_filename_preview(self):
        """Update filename preview."""
        module = self.module_combo.currentData()
        if not module or not self.config_data:
            return
        
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        sheet_num = self.sheet_spin.value()
        use_padding = module.get('use_zero_padding', True)
        
        sheet_label = f"{sheet_type} {sheet_num:02d}" if use_padding else f"{sheet_type} {sheet_num}"
        filename = f"{sheet_label.replace(' ', '_')}_{self.config_data['student_id']}.docx"
        
        self.filename_preview.setText(f"📄  {filename}")
    
    # ==========================================
    # Actions
    # ==========================================
    
    def generate_lab_sheet(self):
        """Generate lab sheet."""
        module = self.module_combo.currentData()
        if not module:
            QMessageBox.warning(self, "No Module", "Please select a module.")
            return
        
        manager = get_template_manager()
        template_id = module.get('template', 'classic')
        
        try:
            template = manager.get_template(template_id)
        except KeyError:
            QMessageBox.critical(self, "Error", f"Template '{template_id}' not found!")
            return
        
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        sheet_num = self.sheet_spin.value()
        use_padding = module.get('use_zero_padding', True)
        sheet_label = f"{sheet_type} {sheet_num:02d}" if use_padding else f"{sheet_type} {sheet_num}"
        
        output_dir = module.get('output_path') or self.global_output_dir
        
        template_logo_path = self.config.config_dir / f"logo_{template_id}.png"
        logo_path = template_logo_path if template_logo_path.exists() else self.config.get_logo_path()
        
        if not logo_path or not logo_path.exists():
            reply = QMessageBox.question(
                self, "No Logo",
                f"No logo for '{template_id}' template. Generate without logo?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            logo_path = None
        
        self.generate_btn.setEnabled(False)
        self.status_label.setText("⏳ Generating lab sheet...")
        self.status_label.setStyleSheet("color: #5b8def; font-weight: 600;")
        
        self.generator_thread = GeneratorThread(
            template, self.config_data['student_name'], self.config_data['student_id'],
            module['name'], module['code'], sheet_label, logo_path, output_dir
        )
        
        self.generator_thread.finished.connect(self.on_generation_complete)
        self.generator_thread.error.connect(self.on_generation_error)
        self.generator_thread.start()
    
    def on_generation_complete(self, file_path):
        """Handle generation success."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText("✓ Lab sheet generated successfully!")
        self.status_label.setStyleSheet("color: #28a745; font-weight: 600;")
        
        reply = QMessageBox.information(
            self, "Success",
            f"Lab sheet generated!\n\nSaved to:\n{file_path}\n\nOpen folder?",
            QMessageBox.Open | QMessageBox.Close
        )
        
        if reply == QMessageBox.Open:
            self.open_folder(os.path.dirname(file_path))
    
    def on_generation_error(self, error_msg):
        """Handle generation error."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText("✗ Generation failed")
        self.status_label.setStyleSheet("color: #d73a49; font-weight: 600;")
        QMessageBox.critical(self, "Error", f"Failed to generate:\n\n{error_msg}")
    
    def change_template(self):
        """Change template for module."""
        from app.ui.template_selector import show_template_selector
        
        module = self.module_combo.currentData()
        if not module:
            return
        
        selected = show_template_selector(module.get('template', 'classic'), self)
        
        if selected and selected != module.get('template'):
            module_index = self.module_combo.currentIndex()
            self.config_data['modules'][module_index]['template'] = selected
            module['template'] = selected
            
            manager = get_template_manager()
            try:
                template = manager.get_template(selected)
                self.template_label.setText(f"Template: {template.template_name}")
            except KeyError:
                self.template_label.setText(f"Template: {selected.title()}")
            
            self.update_logo_for_template(selected)
            self.save_config()
    
    def browse_module_output_path(self):
        """Browse for module output folder."""
        module = self.module_combo.currentData()
        if not module:
            return
        
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder",
            module.get('output_path') or self.global_output_dir
        )
        
        if folder:
            module['output_path'] = folder
            self.output_path_label.setText(folder)
            self.save_config()
    
    def open_output_folder(self):
        """Open output folder."""
        module = self.module_combo.currentData()
        output_dir = module.get('output_path') or self.global_output_dir if module else self.global_output_dir
        self.open_folder(output_dir)
    
    def open_folder(self, folder_path):
        """Open folder in file explorer."""
        if os.name == 'nt':
            os.startfile(folder_path)
        elif os.name == 'posix':
            import subprocess
            subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', folder_path])
    
    def change_global_output_folder(self):
        """Change default output folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Default Output Folder", self.global_output_dir
        )
        
        if folder:
            self.global_output_dir = folder
            self.config_data['global_output_path'] = folder
            self.save_config()
            self.update_output_path_display()
            QMessageBox.information(self, "Success", f"Output folder changed to:\n{folder}")
    
    def edit_configuration(self):
        """Open configuration editor."""
        from app.ui.setup_window import SetupWindow
        
        try:
            setup_window = SetupWindow(self.config, self)
            setup_window.load_existing_config()
            setup_window.setup_complete.connect(self.on_config_updated)
            setup_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open editor:\n\n{e}")
    
    def on_config_updated(self, config_data):
        """Handle configuration update."""
        self.config_data = self.config.load_config()
        self.global_output_dir = self.config_data.get('global_output_path', str(get_output_dir()))
        self.update_student_info_display()
        self.populate_modules()
        
        if self.config_data and self.config_data.get('modules'):
            template_id = self.config_data['modules'][0].get('template', 'classic')
            self.update_logo_for_template(template_id)
    
    def reset_configuration(self):
        """Reset all configuration."""
        reply = QMessageBox.warning(
            self, "Reset Configuration",
            "Reset all configuration? This will delete your data.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.reset_config()
            QMessageBox.information(self, "Reset", "Configuration reset. Please restart.")
            self.close()
    
    def save_config(self):
        """Save current configuration."""
        self.config.save_config(
            self.config_data['student_name'],
            self.config_data['student_id'],
            self.config_data['modules'],
            self.config_data['global_output_path'],
            'light',
            self.config_data.get('default_template', 'classic'),
            self.config_data.get('user_email')
        )
    
    # ==========================================
    # Phase 2: Schedule Management
    # ==========================================
    
    def open_schedule_manager(self):
        """Open schedule management window."""
        # Always create a new window instance
        self.schedule_window = ScheduleWindow(
            schedule_manager=self.schedule_manager,
            config=self.config,
            parent=None  # No parent so it's independent
        )
        self.schedule_window.schedules_updated.connect(self.on_schedules_updated)
        self.schedule_window.show()
        
        # Center the window on screen
        screen = QApplication.primaryScreen().geometry()
        window_geo = self.schedule_window.geometry()
        x = (screen.width() - window_geo.width()) // 2
        y = (screen.height() - window_geo.height()) // 2
        self.schedule_window.move(x, y)
    
    def on_schedules_updated(self):
        """Handle schedule updates."""
        self.schedule_manager.load_schedules()
        self.update_student_info_display()
        
        active_count = len(self.schedule_manager.get_active_schedules())
        self.status_label.setText(f"✓ {active_count} active schedule(s)")
        self.status_label.setStyleSheet("color: #28a745; font-weight: 600;")
    
    # ==========================================
    # OneDrive Integration
    # ==========================================
    
    def on_onedrive_connection_changed(self, connected):
        """Handle OneDrive connection state change."""
        if connected:
            self.status_label.setText("✓ OneDrive connected!")
            self.status_label.setStyleSheet("color: #28a745; font-weight: 600;")
        else:
            self.status_label.setText("OneDrive disconnected")
            self.status_label.setStyleSheet("color: #6a737d; font-weight: 600;")
    
    # ==========================================
    # About Dialog
    # ==========================================
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About Lab Sheet Generator",
            "<h3>Lab Sheet Generator V3.0</h3>"
            "<p>Modern desktop app for automated lab sheet generation.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Clean, modern UI</li>"
            "<li>Multiple templates</li>"
            "<li>Template-specific logos</li>"
            "<li>OneDrive cloud sync</li>"
            "<li>Automated scheduling</li>"
            "</ul>"
        )
