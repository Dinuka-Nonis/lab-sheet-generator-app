"""
OneDrive Connection Widget for Lab Sheet Generator V3.0
Separate widget for OneDrive integration UI
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path
import os


class OneDriveWidget(QWidget):
    """Widget for OneDrive connection and sync controls."""
    
    # Signals
    connection_changed = Signal(bool)  # True if connected, False if disconnected
    sync_completed = Signal(bool)  # True if successful, False if failed
    
    def __init__(self, onedrive_client, sync_manager, config, parent=None):
        super().__init__(parent)
        self.onedrive_client = onedrive_client
        self.sync_manager = sync_manager
        self.config = config
        
        self.init_ui()
        
        # Check if already authenticated
        if self.onedrive_client and self.onedrive_client.authenticate_silent():
            self.update_ui_connected()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Connection status row
        status_layout = QHBoxLayout()
        status_layout.setSpacing(12)
        
        self.status_label = QLabel("● Not connected")
        self.status_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #6a737d;
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Connect/Disconnect button
        self.connect_btn = QPushButton("Connect OneDrive")
        self.connect_btn.setMinimumHeight(44)
        self.connect_btn.setMinimumWidth(180)
        self.connect_btn.setStyleSheet("""
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
        self.connect_btn.clicked.connect(self.handle_connection)
        status_layout.addWidget(self.connect_btn)
        
        layout.addLayout(status_layout)
        
        # User info (hidden initially)
        self.user_info = QLabel()
        self.user_info.setStyleSheet("""
            font-size: 14px;
            color: #586069;
            padding: 8px;
            background-color: #f6f8fa;
            border-radius: 4px;
        """)
        self.user_info.setWordWrap(True)
        self.user_info.setVisible(False)
        layout.addWidget(self.user_info)
        
        # Sync button (hidden initially)
        self.sync_btn = QPushButton("🔄 Sync Configuration Now")
        self.sync_btn.setMinimumHeight(42)
        self.sync_btn.setStyleSheet("""
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
        self.sync_btn.clicked.connect(self.manual_sync)
        self.sync_btn.setVisible(False)
        layout.addWidget(self.sync_btn)
        
        # Last sync info (hidden initially)
        self.last_sync_label = QLabel()
        self.last_sync_label.setStyleSheet("""
            font-size: 13px;
            color: #6a737d;
            padding: 4px;
        """)
        self.last_sync_label.setVisible(False)
        layout.addWidget(self.last_sync_label)
        
        self.setLayout(layout)
    
    def handle_connection(self):
        """Handle connection button click."""
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
                self.update_ui_disconnected()
                self.connection_changed.emit(False)
                
                QMessageBox.information(
                    self,
                    "Disconnected",
                    "OneDrive has been disconnected."
                )
        else:
            # Not connected - authenticate
            QApplication.processEvents()
            
            # Authenticate (this will open browser)
            success = self.onedrive_client.authenticate_interactive()
            
            if success:
                self.update_ui_connected()
                self.connection_changed.emit(True)
                
                # Ensure folder structure
                self.onedrive_client.ensure_folder_structure()
                
                # Initial sync to cloud
                self.sync_manager.sync_to_cloud()
                
                # Sync logo if exists
                logo_path = self.config.get_logo_path()
                if logo_path:
                    self.sync_manager.sync_logo(logo_path)
                
                QMessageBox.information(
                    self,
                    "Connected Successfully",
                    "OneDrive connected successfully!\n\n"
                    "Your configuration has been synced to the cloud.\n"
                    "Lab sheets will now be automatically uploaded to OneDrive."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Connection Failed",
                    "Failed to connect to OneDrive.\n\n"
                    "Please check:\n"
                    "• Internet connection\n"
                    "• Azure configuration\n"
                    "• Microsoft account access"
                )
    
    def update_ui_connected(self):
        """Update UI to show connected state."""
        user_info = self.onedrive_client.get_user_info()
        
        if user_info:
            display_name = user_info.get('displayName', 'User')
            email = user_info.get('userPrincipalName', '')
            
            self.status_label.setText("● Connected")
            self.status_label.setStyleSheet("""
                font-size: 15px;
                font-weight: 600;
                color: #28a745;
            """)
            
            # Load config to get user email
            config_data = self.config.load_config()
            user_email = config_data.get('user_email', 'Not configured')
            
            self.user_info.setText(
                f"🔐 Storage: {email}\n"
                f"📧 Notifications: {user_email}"
            )
            self.user_info.setVisible(True)
            
            self.connect_btn.setText("Disconnect")
            self.connect_btn.setStyleSheet("""
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
            
            self.sync_btn.setVisible(True)
            
            # Show last sync info
            sync_info = self.sync_manager.get_last_sync_info()
            if sync_info:
                from datetime import datetime
                sync_time = datetime.fromisoformat(sync_info['last_sync_time'])
                time_str = sync_time.strftime('%B %d, %Y at %I:%M %p')
                self.last_sync_label.setText(f"Last synced: {time_str}")
                self.last_sync_label.setVisible(True)
    
    def update_ui_disconnected(self):
        """Update UI to show disconnected state."""
        self.status_label.setText("● Not connected")
        self.status_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #6a737d;
        """)
        
        self.user_info.setVisible(False)
        
        self.connect_btn.setText("Connect OneDrive")
        self.connect_btn.setStyleSheet("""
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
        
        self.sync_btn.setVisible(False)
        self.last_sync_label.setVisible(False)
    
    def manual_sync(self):
        """Manually sync configuration to OneDrive."""
        if not self.onedrive_client.is_authenticated():
            QMessageBox.warning(
                self,
                "Not Connected",
                "Please connect to OneDrive first."
            )
            return
        
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("Syncing...")
        QApplication.processEvents()
        
        # Sync config
        config_success = self.sync_manager.sync_to_cloud()
        
        # Try to sync logo from multiple locations
        logo_synced = False
        
        logo_path = self.config.get_logo_path()
        if logo_path and logo_path.exists():
            logo_synced = self.sync_manager.sync_logo(logo_path)
        
        if not logo_synced:
            for template_id in ['classic', 'sliit']:
                template_logo = self.config.config_dir / f"logo_{template_id}.png"
                if template_logo.exists():
                    logo_synced = self.sync_manager.sync_logo(template_logo)
                    break
        
        self.sync_btn.setEnabled(True)
        self.sync_btn.setText("🔄 Sync Configuration Now")
        
        if config_success:
            # Update last sync info
            sync_info = self.sync_manager.get_last_sync_info()
            if sync_info:
                from datetime import datetime
                sync_time = datetime.fromisoformat(sync_info['last_sync_time'])
                time_str = sync_time.strftime('%B %d, %Y at %I:%M %p')
                self.last_sync_label.setText(f"Last synced: {time_str}")
                self.last_sync_label.setVisible(True)
            
            self.sync_completed.emit(True)
            
            QMessageBox.information(
                self,
                "Sync Successful",
                f"Configuration synced successfully!\n"
                f"{'Logo synced too!' if logo_synced else 'No logo found to sync.'}"
            )
        else:
            self.sync_completed.emit(False)
            
            QMessageBox.warning(
                self,
                "Sync Failed",
                "Failed to sync to OneDrive.\n"
                "Please check your internet connection."
            )


class OneDriveSetupWidget(QWidget):
    """Widget shown when OneDrive is not configured."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Warning message
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
        layout.addWidget(info_label)
        
        # Setup guide button
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
        layout.addWidget(setup_btn)
        
        self.setLayout(layout)
    
    def open_setup_guide(self):
        """Open Azure setup guide."""
        guide_path = Path(__file__).parent.parent.parent / "AZURE_SETUP_GUIDE.md"
        
        if guide_path.exists():
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
