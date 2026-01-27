from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QFileDialog, QMenu
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QPixmap
from app.generator import generate_lab_sheet
from app.utils.paths import get_output_dir
import os


class GeneratorThread(QThread):
    """Thread for generating lab sheets without blocking UI."""
    
    finished = Signal(str)  # Emits the output file path
    error = Signal(str)  # Emits error message
    
    def __init__(self, student_name, student_id, module_name, module_code, 
                 practical_number, logo_path, output_dir):
        super().__init__()
        self.student_name = student_name
        self.student_id = student_id
        self.module_name = module_name
        self.module_code = module_code
        self.practical_number = practical_number
        self.logo_path = logo_path
        self.output_dir = output_dir
    
    def run(self):
        """Generate the lab sheet."""
        try:
            # Generate in the output directory
            original_dir = os.getcwd()
            os.chdir(self.output_dir)
            
            output_file = generate_lab_sheet(
                student_name=self.student_name,
                student_id=self.student_id,
                module_name=self.module_name,
                module_code=self.module_code,
                practical_number=self.practical_number,
                logo_path=str(self.logo_path) if self.logo_path else None
            )
            
            os.chdir(original_dir)
            
            # Return full path
            full_path = os.path.join(self.output_dir, output_file)
            self.finished.emit(full_path)
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for generating lab sheets."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.config_data = config.load_config()
        self.global_output_dir = self.config_data.get('global_output_path', str(get_output_dir()))
        self.generator_thread = None
        
        self.setWindowTitle("Lab Sheet Generator")
        self.setMinimumSize(700, 600)
        
        self.init_ui()
        self.init_menu()
    
    def init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()
        
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
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("Generate Lab Sheet")
        header.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #156082;
            margin: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Student Info Display
        info_group = QGroupBox("Your Information")
        info_layout = QVBoxLayout()
        
        self.student_info_label = QLabel()
        self.student_info_label.setStyleSheet("font-size: 13px; padding: 5px;")
        self.update_student_info_display()
        info_layout.addWidget(self.student_info_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Logo Status
        logo_group = QGroupBox("University Logo")
        logo_layout = QHBoxLayout()
        
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(88, 84)
        self.logo_preview.setStyleSheet("border: 1px solid #ccc; background: #f5f5f5;")
        self.logo_preview.setAlignment(Qt.AlignCenter)
        
        logo_path = self.config.get_logo_path()
        if logo_path and logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
            self.logo_status_label = QLabel("✓ Logo loaded")
            self.logo_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.logo_preview.setText("No Logo")
            self.logo_status_label = QLabel("⚠ No logo set")
            self.logo_status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addWidget(self.logo_status_label)
        logo_layout.addStretch()
        
        logo_group.setLayout(logo_layout)
        main_layout.addWidget(logo_group)
        
        # Generator Section
        generator_group = QGroupBox("Generate Lab Sheet")
        generator_layout = QFormLayout()
        generator_layout.setSpacing(15)
        
        # Module selection
        self.module_combo = QComboBox()
        self.module_combo.currentIndexChanged.connect(self.on_module_changed)
        generator_layout.addRow("Select Module:", self.module_combo)
        
        # Sheet type display
        self.sheet_type_label = QLabel("Practical")
        self.sheet_type_label.setStyleSheet("font-weight: bold; color: #156082; font-size: 12px;")
        generator_layout.addRow("Sheet Type:", self.sheet_type_label)
        
        # Sheet number
        self.sheet_spin = QSpinBox()
        self.sheet_spin.setMinimum(1)
        self.sheet_spin.setMaximum(99)
        self.sheet_spin.setValue(1)
        self.sheet_spin.valueChanged.connect(self.update_filename_preview)
        generator_layout.addRow("Sheet Number:", self.sheet_spin)
        
        # Output path with browse button
        output_layout = QHBoxLayout()
        self.output_path_label = QLabel()
        self.output_path_label.setStyleSheet("color: #333; font-size: 11px;")
        self.output_path_label.setWordWrap(True)
        output_layout.addWidget(self.output_path_label, 1)
        
        browse_output_btn = QPushButton("Browse...")
        browse_output_btn.setMaximumWidth(80)
        browse_output_btn.clicked.connect(self.browse_module_output_path)
        output_layout.addWidget(browse_output_btn)
        
        output_widget = QWidget()
        output_widget.setLayout(output_layout)
        generator_layout.addRow("Output Path:", output_widget)
        
        # Filename preview
        self.filename_preview = QLabel()
        self.filename_preview.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10px;
            color: #666;
        """)
        self.filename_preview.setWordWrap(True)
        generator_layout.addRow("Preview:", self.filename_preview)
        
        generator_group.setLayout(generator_layout)
        main_layout.addWidget(generator_group)
        
        # Generate button
        main_layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.generate_btn = QPushButton("Generate Lab Sheet")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #156082;
                color: white;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1a7599;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_lab_sheet)
        button_layout.addWidget(self.generate_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; padding: 10px;")
        main_layout.addWidget(self.status_label)
        
        central_widget.setLayout(main_layout)
        
        # Populate modules
        self.populate_modules()
    
    def update_student_info_display(self):
        """Update the student information display."""
        name = self.config_data.get('student_name', 'N/A')
        student_id = self.config_data.get('student_id', 'N/A')
        modules_count = len(self.config_data.get('modules', []))
        
        info_text = f"<b>Name:</b> {name}<br><b>Student ID:</b> {student_id}<br><b>Modules:</b> {modules_count} module(s)"
        self.student_info_label.setText(info_text)
    
    def populate_modules(self):
        """Populate the module dropdown."""
        self.module_combo.clear()
        modules = self.config_data.get('modules', [])
        
        if not modules:
            self.module_combo.addItem("No modules configured")
            self.generate_btn.setEnabled(False)
        else:
            for module in modules:
                display_text = f"{module['name']} ({module['code']})"
                self.module_combo.addItem(display_text, module)
            self.generate_btn.setEnabled(True)
            
            # Trigger update for first module
            if modules:
                self.on_module_changed(0)
    
    def on_module_changed(self, index):
        """Called when module selection changes."""
        module = self.module_combo.currentData()
        if module:
            # Update sheet type label
            sheet_type = module.get('sheet_type', 'Practical')
            if sheet_type == 'Custom':
                sheet_type = module.get('custom_sheet_type', 'Sheet')
            self.sheet_type_label.setText(sheet_type)
            
            # Update output path
            self.update_output_path_display()
            
            # Update filename preview
            self.update_filename_preview()
    
    def update_output_path_display(self):
        """Update the output path display based on selected module."""
        module = self.module_combo.currentData()
        if not module:
            return
        
        output_path = module.get('output_path')
        if output_path:
            self.output_path_label.setText(output_path)
            self.output_path_label.setStyleSheet("color: #156082; font-weight: bold; font-size: 11px;")
        else:
            self.output_path_label.setText(f"{self.global_output_dir} (default)")
            self.output_path_label.setStyleSheet("color: #666; font-size: 11px;")
    
    def update_filename_preview(self):
        """Update the filename preview."""
        module = self.module_combo.currentData()
        if not module:
            self.filename_preview.setText("Select a module to see preview")
            return
        
        # Get sheet type and number
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        sheet_num = self.sheet_spin.value()
        student_id = self.config_data.get('student_id', 'UNKNOWN')
        
        # Format with zero padding if enabled
        use_padding = module.get('use_zero_padding', True)
        num_str = f"{sheet_num:02d}" if use_padding else str(sheet_num)
        
        # Create filename
        filename = f"{sheet_type.replace(' ', '_')}_{num_str}_{student_id}.docx"
        
        self.filename_preview.setText(f"Will be saved as: {filename}")
    
    def browse_module_output_path(self):
        """Browse for output path for current module."""
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
            # Update module data
            module['output_path'] = folder
            
            # Update display
            self.update_output_path_display()
            
            # Save config
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                self.config_data.get('global_output_path')
            )
            
            # Reload config
            self.config_data = self.config.load_config()
            
            QMessageBox.information(
                self,
                "Path Updated",
                f"Output path for {module['name']} has been updated to:\n{folder}"
            )
    
    def generate_lab_sheet(self):
        """Generate the lab sheet document."""
        # Check if modules exist
        if self.module_combo.count() == 0 or self.module_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "No Modules",
                "Please add modules in the configuration first."
            )
            return
        
        # Get selected module
        module = self.module_combo.currentData()
        sheet_num = self.sheet_spin.value()
        
        # Determine sheet type text
        sheet_type = module.get('sheet_type', 'Practical')
        if sheet_type == 'Custom':
            sheet_type = module.get('custom_sheet_type', 'Sheet')
        
        # Format number
        use_padding = module.get('use_zero_padding', True)
        num_str = f"{sheet_num:02d}" if use_padding else str(sheet_num)
        sheet_label = f"{sheet_type} {num_str}"
        
        # Determine output directory
        output_dir = module.get('output_path') or self.global_output_dir
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Get logo path
        logo_path = self.config.get_logo_path()
        if not logo_path or not logo_path.exists():
            reply = QMessageBox.question(
                self,
                "No Logo",
                "No logo is configured. Generate without logo?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
            logo_path = None
        
        # Disable button and show status
        self.generate_btn.setEnabled(False)
        self.status_label.setText("Generating lab sheet...")
        self.status_label.setStyleSheet("color: #156082; font-size: 12px; padding: 10px;")
        
        # Create and start generator thread
        self.generator_thread = GeneratorThread(
            student_name=self.config_data['student_name'],
            student_id=self.config_data['student_id'],
            module_name=module['name'],
            module_code=module['code'],
            practical_number=sheet_label,
            logo_path=logo_path,
            output_dir=output_dir
        )
        
        self.generator_thread.finished.connect(self.on_generation_complete)
        self.generator_thread.error.connect(self.on_generation_error)
        self.generator_thread.start()
    
    def on_generation_complete(self, file_path):
        """Called when generation is complete."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText(f"✓ Lab sheet generated successfully!")
        self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 12px; padding: 10px;")
        
        # Show success dialog
        reply = QMessageBox.information(
            self,
            "Success",
            f"Lab sheet generated successfully!\n\nSaved to:\n{file_path}\n\nWould you like to open the folder?",
            QMessageBox.Open | QMessageBox.Close
        )
        
        if reply == QMessageBox.Open:
            # Open the specific folder where the file was saved
            folder_path = os.path.dirname(file_path)
            self.open_folder(folder_path)
    
    def on_generation_error(self, error_msg):
        """Called when generation fails."""
        self.generate_btn.setEnabled(True)
        self.status_label.setText("✗ Generation failed")
        self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 12px; padding: 10px;")
        
        QMessageBox.critical(
            self,
            "Error",
            f"Failed to generate lab sheet:\n\n{error_msg}"
        )
    
    def open_output_folder(self):
        """Open the current module's output folder or default folder."""
        module = self.module_combo.currentData()
        if module:
            output_dir = module.get('output_path') or self.global_output_dir
        else:
            output_dir = self.global_output_dir
        
        self.open_folder(output_dir)
    
    def open_folder(self, folder_path):
        """Open a folder in the file explorer."""
        if os.name == 'nt':  # Windows
            os.startfile(folder_path)
        elif os.name == 'posix':  # macOS/Linux
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
            
            # Update config
            self.config_data['global_output_path'] = folder
            self.config.save_config(
                self.config_data['student_name'],
                self.config_data['student_id'],
                self.config_data['modules'],
                folder
            )
            
            # Update display if current module uses default
            self.update_output_path_display()
            
            QMessageBox.information(
                self,
                "Output Folder Changed",
                f"Default output folder changed to:\n{folder}\n\nModules without a specific output path will use this location."
            )
    
    def edit_configuration(self):
        """Open setup wizard to edit configuration."""
        from app.ui.setup_ui import SetupWindow
        
        setup_window = SetupWindow(self.config)
        
        # Pre-fill with existing data
        setup_window.name_input.setText(self.config_data.get('student_name', ''))
        setup_window.id_input.setText(self.config_data.get('student_id', ''))
        
        # Pre-fill modules
        setup_window.modules = self.config_data.get('modules', []).copy()
        setup_window.update_module_list_display()
        
        # Pre-fill logo
        logo_path = self.config.get_logo_path()
        if logo_path and logo_path.exists():
            setup_window.logo_path = str(logo_path)
            setup_window.logo_label.setText(logo_path.name)
            setup_window.logo_label.setStyleSheet("color: green;")
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(110, 105, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            setup_window.logo_preview.setPixmap(scaled_pixmap)
        
        def on_setup_complete(config_data):
            # Reload config
            self.config_data = self.config.load_config()
            self.global_output_dir = self.config_data.get('global_output_path', str(get_output_dir()))
            self.update_student_info_display()
            self.populate_modules()
            
            # Update logo preview
            logo_path = self.config.get_logo_path()
            if logo_path and logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                scaled_pixmap = pixmap.scaled(88, 84, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.logo_preview.setPixmap(scaled_pixmap)
                self.logo_status_label.setText("✓ Logo loaded")
                self.logo_status_label.setStyleSheet("color: green; font-weight: bold;")
        
        setup_window.setup_complete.connect(on_setup_complete)
        setup_window.show()
    
    def reset_configuration(self):
        """Reset all configuration."""
        reply = QMessageBox.warning(
            self,
            "Reset Configuration",
            "Are you sure you want to reset all configuration?\n\nThis will delete your student info, modules, and logo.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.reset_config()
            QMessageBox.information(
                self,
                "Configuration Reset",
                "Configuration has been reset. The application will now close.\n\nPlease restart to set up again."
            )
            self.close()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Lab Sheet Generator",
            "<h3>Lab Sheet Generator</h3>"
            "<p>Version 1.1.0</p>"
            "<p>A desktop application for university students to generate "
            "lab sheet templates automatically.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Automated lab sheet generation</li>"
            "<li>Custom university logo support</li>"
            "<li>Multiple module management</li>"
            "<li>Per-module output paths</li>"
            "<li>Configurable sheet types (Lab, Practical, Worksheet, etc.)</li>"
            "<li>Professional document formatting</li>"
            "</ul>"
            "<p><b>New in v1.1:</b></p>"
            "<ul>"
            "<li>Per-module output path configuration</li>"
            "<li>Customizable sheet types per module</li>"
            "<li>Filename preview before generation</li>"
            "<li>Enhanced module management</li>"
            "</ul>"
        )