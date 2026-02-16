"""
Cloud settings and management dialog
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QGroupBox,
    QFormLayout, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class CloudSettingsDialog(QDialog):
    """Dialog for cloud service configuration."""
    
    def __init__(self, config, api_client, parent=None):
        super().__init__(parent)
        self.config = config
        self.api_client = api_client
        
        self.setWindowTitle("Cloud Service Settings")
        self.resize(600, 500)
        self.setModal(True)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Cloud Service Configuration")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Connection settings
        conn_group = QGroupBox("Connection")
        conn_layout = QFormLayout()
        conn_layout.setSpacing(12)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://your-app.onrender.com")
        self.url_input.setMinimumHeight(40)
        conn_layout.addRow("Cloud URL:", self.url_input)
        
        # Test button
        test_btn = QPushButton("Test Connection")
        test_btn.setMinimumHeight(40)
        test_btn.clicked.connect(self.test_connection)
        conn_layout.addRow("", test_btn)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Account info
        if self.api_client.is_authenticated():
            account_group = QGroupBox("Account")
            account_layout = QVBoxLayout()
            account_layout.setSpacing(10)
            
            user_info = self.api_client.user_info or {}
            
            info_text = f"""
<b>Name:</b> {user_info.get('name', 'N/A')}<br>
<b>Student ID:</b> {user_info.get('student_id', 'N/A')}<br>
<b>Modules:</b> {user_info.get('modules_count', 0)}<br>
<b>Schedules:</b> {user_info.get('schedules_count', 0)}
            """
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("""
                background-color: #f6f8fa;
                padding: 15px;
                border-radius: 6px;
                font-size: 13px;
            """)
            account_layout.addWidget(info_label)
            
            logout_btn = QPushButton("Logout")
            logout_btn.setMinimumHeight(40)
            logout_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d73a49;
                    color: white;
                    font-weight: 600;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #cb2431;
                }
            """)
            logout_btn.clicked.connect(self.handle_logout)
            account_layout.addWidget(logout_btn)
            
            account_group.setLayout(account_layout)
            layout.addWidget(account_group)
        
        # Buttons
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        save_btn = QPushButton("Save")
        save_btn.setMinimumHeight(45)
        save_btn.setMinimumWidth(120)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                font-size: 14px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0256c2;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Load current settings."""
        cloud_url = getattr(self.config, 'cloud_url', '') or ''
        self.url_input.setText(cloud_url)
    
    def save_settings(self):
        """Save settings."""
        url = self.url_input.text().strip()
        
        if url and not url.startswith('http'):
            QMessageBox.warning(
                self,
                "Invalid URL",
                "URL must start with http:// or https://"
            )
            return
        
        # Save to config
        self.config.save_cloud_settings(bool(url), url)
        
        # Update API client
        if url:
            self.api_client.base_url = url.rstrip('/')
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        self.accept()
    
    def test_connection(self):
        """Test connection to cloud service."""
        url = self.url_input.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a cloud URL")
            return
        
        # Temporarily set URL for testing
        old_url = self.api_client.base_url
        self.api_client.base_url = url.rstrip('/')
        
        try:
            if self.api_client.test_connection():
                QMessageBox.information(
                    self,
                    "Success",
                    "✓ Connected to cloud service successfully!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Connection Failed",
                    "Could not connect to cloud service.\n\nPlease check:\n"
                    "• URL is correct\n"
                    "• Service is running\n"
                    "• Internet connection"
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Connection test failed:\n{str(e)}"
            )
        
        finally:
            # Restore original URL
            self.api_client.base_url = old_url
    
    def handle_logout(self):
        """Handle logout."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?\n\nYou will need to login again to use cloud features.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.api_client.logout()
            QMessageBox.information(self, "Success", "Logged out successfully!")
            self.accept()
