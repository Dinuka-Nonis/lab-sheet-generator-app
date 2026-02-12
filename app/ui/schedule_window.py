"""
Schedule Management Window for Lab Sheet Generator V3.0
UI for creating and managing lab sheet generation schedules
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QFormLayout, QComboBox, QSpinBox, QTimeEdit,
    QCheckBox, QGroupBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, QTime
from PySide6.QtGui import QColor
from datetime import time


class ScheduleDialog(QDialog):
    """Dialog for creating/editing a schedule."""
    
    def __init__(self, parent=None, schedule=None, modules=None):
        super().__init__(parent)
        self.schedule = schedule
        self.modules = modules or []
        
        self.setWindowTitle("Add Schedule" if not schedule else "Edit Schedule")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        self.init_ui()
        
        if schedule:
            self.load_schedule_data()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Basic Info Group
        basic_group = QGroupBox("Lab Session Details")
        basic_group.setStyleSheet("QGroupBox { font-size: 15px; font-weight: 600; }")
        basic_layout = QFormLayout()
        basic_layout.setSpacing(14)
        
        # Module selection
        self.module_combo = QComboBox()
        self.module_combo.setMinimumHeight(44)
        self.module_combo.setStyleSheet("font-size: 14px;")
        
        if self.modules:
            for module in self.modules:
                display_text = f"{module['name']} ({module['code']})"
                self.module_combo.addItem(display_text, module)
        else:
            self.module_combo.addItem("No modules configured", None)
        
        basic_layout.addRow("<b>Module:</b>", self.module_combo)
        
        # Day of week
        self.day_combo = QComboBox()
        self.day_combo.setMinimumHeight(44)
        self.day_combo.setStyleSheet("font-size: 14px;")
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.day_combo.addItems(days)
        basic_layout.addRow("<b>Day of Week:</b>", self.day_combo)
        
        # Lab time
        self.time_edit = QTimeEdit()
        self.time_edit.setMinimumHeight(44)
        self.time_edit.setDisplayFormat("hh:mm AP")
        self.time_edit.setTime(QTime(10, 0))  # Default 10:00 AM
        self.time_edit.setStyleSheet("font-size: 14px;")
        basic_layout.addRow("<b>Lab Time:</b>", self.time_edit)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Generation Settings Group
        gen_group = QGroupBox("Generation Settings")
        gen_group.setStyleSheet("QGroupBox { font-size: 15px; font-weight: 600; }")
        gen_layout = QFormLayout()
        gen_layout.setSpacing(14)
        
        # Generate before
        self.before_spin = QSpinBox()
        self.before_spin.setMinimumHeight(44)
        self.before_spin.setMinimum(5)
        self.before_spin.setMaximum(1440)  # 24 hours
        self.before_spin.setValue(60)
        self.before_spin.setSuffix(" minutes")
        self.before_spin.setStyleSheet("font-size: 14px;")
        gen_layout.addRow("<b>Generate Before Lab:</b>", self.before_spin)
        
        # Starting practical number
        self.practical_spin = QSpinBox()
        self.practical_spin.setMinimumHeight(44)
        self.practical_spin.setMinimum(1)
        self.practical_spin.setMaximum(99)
        self.practical_spin.setValue(1)
        self.practical_spin.setStyleSheet("font-size: 14px;")
        gen_layout.addRow("<b>Current Practical Number:</b>", self.practical_spin)
        
        gen_group.setLayout(gen_layout)
        layout.addWidget(gen_group)
        
        # Options Group
        options_group = QGroupBox("Options")
        options_group.setStyleSheet("QGroupBox { font-size: 15px; font-weight: 600; }")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)
        
        self.auto_increment_check = QCheckBox("Auto-increment practical number after each generation")
        self.auto_increment_check.setChecked(True)
        self.auto_increment_check.setStyleSheet("font-size: 14px;")
        options_layout.addWidget(self.auto_increment_check)
        
        self.zero_padding_check = QCheckBox("Use zero padding (e.g., '01' instead of '1')")
        self.zero_padding_check.setChecked(True)
        self.zero_padding_check.setStyleSheet("font-size: 14px;")
        options_layout.addWidget(self.zero_padding_check)
        
        self.upload_check = QCheckBox("Upload to OneDrive after generation")
        self.upload_check.setChecked(True)
        self.upload_check.setStyleSheet("font-size: 14px;")
        options_layout.addWidget(self.upload_check)
        
        self.email_check = QCheckBox("Send email notification when ready")
        self.email_check.setChecked(True)
        self.email_check.setStyleSheet("font-size: 14px;")
        options_layout.addWidget(self.email_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("Save Schedule")
        button_box.button(QDialogButtonBox.Ok).setMinimumHeight(44)
        button_box.button(QDialogButtonBox.Cancel).setMinimumHeight(44)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_schedule_data(self):
        """Load existing schedule data."""
        if not self.schedule:
            return
        
        # Find module in combo
        for i in range(self.module_combo.count()):
            module = self.module_combo.itemData(i)
            if module and module.get('code') == self.schedule.module_code:
                self.module_combo.setCurrentIndex(i)
                break
        
        # Set day
        self.day_combo.setCurrentIndex(self.schedule.day_of_week)
        
        # Set time
        q_time = QTime(self.schedule.lab_time.hour, self.schedule.lab_time.minute)
        self.time_edit.setTime(q_time)
        
        # Set generation settings
        self.before_spin.setValue(self.schedule.generate_before_minutes)
        self.practical_spin.setValue(self.schedule.current_practical_number)
        
        # Set options
        self.auto_increment_check.setChecked(self.schedule.auto_increment)
        self.zero_padding_check.setChecked(self.schedule.use_zero_padding)
        self.upload_check.setChecked(self.schedule.upload_to_onedrive)
        self.email_check.setChecked(self.schedule.send_confirmation)
    
    def get_schedule_data(self):
        """Get schedule data from form."""
        module = self.module_combo.currentData()
        
        if not module:
            return None
        
        q_time = self.time_edit.time()
        lab_time = time(q_time.hour(), q_time.minute())
        
        data = {
            'module_code': module['code'],
            'module_name': module['name'],
            'day_of_week': self.day_combo.currentIndex(),
            'lab_time': lab_time,
            'generate_before_minutes': self.before_spin.value(),
            'current_practical_number': self.practical_spin.value(),
            'auto_increment': self.auto_increment_check.isChecked(),
            'use_zero_padding': self.zero_padding_check.isChecked(),
            'template_id': module.get('template', 'classic'),
            'sheet_type': module.get('sheet_type', 'Practical'),
            'upload_to_onedrive': self.upload_check.isChecked(),
            'send_confirmation': self.email_check.isChecked()
        }
        
        return data


class ScheduleWindow(QWidget):
    """Window for managing lab sheet generation schedules."""
    
    schedules_updated = Signal()
    
    def __init__(self, schedule_manager, config, parent=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.config = config
        
        self.setWindowTitle("Manage Lab Schedules")
        self.setMinimumSize(900, 600)
        
        self.init_ui()
        self.load_schedules()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        title = QLabel("Lab Sheet Schedules")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #1a1a1a;
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Automate lab sheet generation for your modules")
        subtitle.setStyleSheet("font-size: 15px; color: #586069;")
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Info box
        info_box = QLabel(
            "💡 Schedules will automatically generate lab sheets at the specified time. "
            "Generated sheets will be uploaded to your OneDrive for easy access from lab computers."
        )
        info_box.setWordWrap(True)
        info_box.setStyleSheet("""
            background-color: #e8f4fd;
            border: 1px solid #0366d6;
            border-radius: 6px;
            padding: 12px;
            font-size: 14px;
            color: #0366d6;
        """)
        layout.addWidget(info_box)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Module", "Day", "Time", "Next Generation", 
            "Practical #", "Status", "Actions"
        ])
        
        # Table styling
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f6f8fa;
                padding: 10px;
                border: none;
                font-weight: 600;
                font-size: 14px;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Schedule")
        add_btn.setMinimumHeight(44)
        add_btn.setMinimumWidth(150)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_btn.clicked.connect(self.add_schedule)
        button_layout.addWidget(add_btn)
        
        button_layout.addStretch()
        
        sync_btn = QPushButton("🔄 Sync to OneDrive")
        sync_btn.setMinimumHeight(44)
        sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0256b8;
            }
        """)
        sync_btn.clicked.connect(self.sync_schedules)
        button_layout.addWidget(sync_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(44)
        close_btn.setMinimumWidth(100)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6a737d;
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #586069;
            }
        """)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_schedules(self):
        """Load schedules into table."""
        schedules = self.schedule_manager.get_all_schedules()
        
        self.table.setRowCount(len(schedules))
        
        for row, schedule in enumerate(schedules):
            # Module
            module_item = QTableWidgetItem(f"{schedule.module_name}\n({schedule.module_code})")
            module_item.setData(Qt.UserRole, schedule.id)
            self.table.setItem(row, 0, module_item)
            
            # Day
            day_item = QTableWidgetItem(schedule.get_day_name())
            self.table.setItem(row, 1, day_item)
            
            # Time
            time_item = QTableWidgetItem(schedule.get_formatted_time())
            self.table.setItem(row, 2, time_item)
            
            # Next generation
            next_gen = self.schedule_manager.get_next_generation_time_str(schedule)
            next_item = QTableWidgetItem(next_gen)
            self.table.setItem(row, 3, next_item)
            
            # Practical number
            prac_num = f"#{schedule.get_practical_number_str()}"
            prac_item = QTableWidgetItem(prac_num)
            self.table.setItem(row, 4, prac_item)
            
            # Status
            status_item = QTableWidgetItem(schedule.status.upper())
            if schedule.status == "active":
                status_item.setForeground(QColor(40, 167, 69))  # Green
            elif schedule.status == "paused":
                status_item.setForeground(QColor(255, 165, 0))  # Orange
            else:
                status_item.setForeground(QColor(220, 53, 69))  # Red
            self.table.setItem(row, 5, status_item)
            
            # Actions - create button widget
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            # Edit button
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Edit schedule")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked, s=schedule: self.edit_schedule(s))
            actions_layout.addWidget(edit_btn)
            
            # Pause/Resume button
            if schedule.is_active():
                pause_btn = QPushButton("⏸️")
                pause_btn.setToolTip("Pause schedule")
                pause_btn.setMaximumWidth(40)
                pause_btn.clicked.connect(lambda checked, sid=schedule.id: self.pause_schedule(sid))
                actions_layout.addWidget(pause_btn)
            else:
                resume_btn = QPushButton("▶️")
                resume_btn.setToolTip("Resume schedule")
                resume_btn.setMaximumWidth(40)
                resume_btn.clicked.connect(lambda checked, sid=schedule.id: self.resume_schedule(sid))
                actions_layout.addWidget(resume_btn)
            
            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Delete schedule")
            delete_btn.setMaximumWidth(40)
            delete_btn.clicked.connect(lambda checked, sid=schedule.id: self.delete_schedule(sid))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 6, actions_widget)
            
            # Set row height
            self.table.setRowHeight(row, 60)
    
    def add_schedule(self):
        """Add new schedule."""
        config_data = self.config.load_config()
        modules = config_data.get('modules', [])
        
        if not modules:
            QMessageBox.warning(
                self,
                "No Modules",
                "Please add modules in Settings → Edit Configuration first."
            )
            return
        
        dialog = ScheduleDialog(self, modules=modules)
        
        if dialog.exec():
            data = dialog.get_schedule_data()
            if data:
                self.schedule_manager.create_schedule(**data)
                self.load_schedules()
                self.schedules_updated.emit()
                
                QMessageBox.information(
                    self,
                    "Schedule Created",
                    f"Schedule for {data['module_name']} created successfully!\n\n"
                    f"Lab sheets will be generated automatically every "
                    f"{dialog.day_combo.currentText()} at "
                    f"{dialog.time_edit.time().toString('hh:mm AP')}."
                )
    
    def edit_schedule(self, schedule):
        """Edit existing schedule."""
        config_data = self.config.load_config()
        modules = config_data.get('modules', [])
        
        dialog = ScheduleDialog(self, schedule=schedule, modules=modules)
        
        if dialog.exec():
            data = dialog.get_schedule_data()
            if data:
                # Update schedule with new data
                for key, value in data.items():
                    setattr(schedule, key, value)
                
                self.schedule_manager.update_schedule(schedule)
                self.load_schedules()
                self.schedules_updated.emit()
                
                QMessageBox.information(
                    self,
                    "Schedule Updated",
                    f"Schedule for {schedule.module_name} updated successfully!"
                )
    
    def delete_schedule(self, schedule_id):
        """Delete schedule."""
        schedule = self.schedule_manager.get_schedule_by_id(schedule_id)
        
        if not schedule:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Schedule",
            f"Are you sure you want to delete the schedule for {schedule.module_name}?\n\n"
            f"This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.schedule_manager.delete_schedule(schedule_id)
            self.load_schedules()
            self.schedules_updated.emit()
            
            QMessageBox.information(
                self,
                "Schedule Deleted",
                f"Schedule for {schedule.module_name} has been deleted."
            )
    
    def pause_schedule(self, schedule_id):
        """Pause schedule."""
        self.schedule_manager.pause_schedule(schedule_id)
        self.load_schedules()
        self.schedules_updated.emit()
    
    def resume_schedule(self, schedule_id):
        """Resume schedule."""
        self.schedule_manager.resume_schedule(schedule_id)
        self.load_schedules()
        self.schedules_updated.emit()
    
    def sync_schedules(self):
        """Sync schedules to OneDrive."""
        success = self.schedule_manager.sync_to_cloud()
        
        if success:
            QMessageBox.information(
                self,
                "Sync Successful",
                "Schedules synced to OneDrive successfully!"
            )
        else:
            QMessageBox.warning(
                self,
                "Sync Failed",
                "Failed to sync schedules to OneDrive.\n"
                "Make sure you're connected to OneDrive."
            )