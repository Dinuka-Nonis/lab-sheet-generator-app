"""
Cloud authentication window for desktop app
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QTabWidget,
    QWidget, QFormLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class CloudAuthDialog(QDialog):
    """Dialog for cloud login and registration."""
    
    authenticated = Signal()  # Emitted when user successfully logs in
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        
        self.setWindowTitle("Cloud Service Login")
        self.resize(500, 450)
        self.setModal(True)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Lab Sheet Generator Cloud")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Connect to cloud service for automated scheduling")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #586069; font-size: 13px;")
        layout.addWidget(subtitle)

        # ── URL warning banner ────────────────────────────────────────────────
        url = self.api_client.base_url
        is_localhost = 'localhost' in url or '127.0.0.1' in url

        if is_localhost:
            warn = QLabel(
                f"⚠️  Cloud URL is set to <b>{url}</b><br>"
                "You need to set your PythonAnywhere URL first.<br>"
                "Go to  <b>Cloud → Cloud Settings</b>  and enter:<br>"
                "<b>http://DinukaNonis.pythonanywhere.com</b>"
            )
            warn.setWordWrap(True)
            warn.setTextFormat(Qt.RichText)
            warn.setStyleSheet("""
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                color: #856404;
            """)
            layout.addWidget(warn)
        else:
            # Show current URL so user knows where they're connecting
            url_label = QLabel(f"🌐  Connecting to: <b>{url}</b>")
            url_label.setTextFormat(Qt.RichText)
            url_label.setStyleSheet("""
                background: #d4edda;
                border: 1px solid #28a745;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #155724;
            """)
            layout.addWidget(url_label)
        # ─────────────────────────────────────────────────────────────────────

        # Tabs for Login/Register
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d1d5da;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: #0366d6;
                color: white;
            }
        """)
        
        # Login tab
        login_widget = QWidget()
        login_layout = QVBoxLayout()
        login_layout.setSpacing(15)
        login_layout.setContentsMargins(20, 20, 20, 20)
        
        login_form = QFormLayout()
        login_form.setSpacing(12)
        
        self.login_student_id = QLineEdit()
        self.login_student_id.setPlaceholderText("e.g., IT12345")
        self.login_student_id.setMinimumHeight(40)
        login_form.addRow("Student ID:", self.login_student_id)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setMinimumHeight(40)
        self.login_password.returnPressed.connect(self.handle_login)
        login_form.addRow("Password:", self.login_password)
        
        login_layout.addLayout(login_form)
        
        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(45)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #0366d6;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0256c2;
            }
            QPushButton:pressed {
                background-color: #024ba8;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        login_layout.addWidget(login_btn)
        
        login_widget.setLayout(login_layout)
        tabs.addTab(login_widget, "Login")
        
        # Register tab
        register_widget = QWidget()
        register_layout = QVBoxLayout()
        register_layout.setSpacing(15)
        register_layout.setContentsMargins(20, 20, 20, 20)
        
        register_form = QFormLayout()
        register_form.setSpacing(12)
        
        self.register_name = QLineEdit()
        self.register_name.setPlaceholderText("Your full name")
        self.register_name.setMinimumHeight(40)
        register_form.addRow("Name:", self.register_name)
        
        self.register_student_id = QLineEdit()
        self.register_student_id.setPlaceholderText("e.g., IT12345")
        self.register_student_id.setMinimumHeight(40)
        register_form.addRow("Student ID:", self.register_student_id)
        
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("your@university.lk")
        self.register_email.setMinimumHeight(40)
        register_form.addRow("Email:", self.register_email)
        
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Choose a password")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setMinimumHeight(40)
        register_form.addRow("Password:", self.register_password)
        
        self.register_confirm = QLineEdit()
        self.register_confirm.setPlaceholderText("Confirm password")
        self.register_confirm.setEchoMode(QLineEdit.Password)
        self.register_confirm.setMinimumHeight(40)
        self.register_confirm.returnPressed.connect(self.handle_register)
        register_form.addRow("Confirm:", self.register_confirm)
        
        register_layout.addLayout(register_form)
        
        register_btn = QPushButton("Register")
        register_btn.setMinimumHeight(45)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #239c3b;
            }
            QPushButton:pressed {
                background-color: #1e8e32;
            }
        """)
        register_btn.clicked.connect(self.handle_register)
        register_layout.addWidget(register_btn)
        
        register_widget.setLayout(register_layout)
        tabs.addTab(register_widget, "Register")
        
        layout.addWidget(tabs)
        
        # Note about email
        note = QLabel("💡 Use your university email to receive lab sheet notifications")
        note.setStyleSheet("""
            background-color: #f6f8fa;
            padding: 12px;
            border-radius: 6px;
            color: #586069;
            font-size: 12px;
        """)
        note.setWordWrap(True)
        layout.addWidget(note)
        
        self.setLayout(layout)
    
    def _check_url(self):
        """Return True if URL is valid (not localhost). Show warning if not."""
        url = self.api_client.base_url
        if 'localhost' in url or '127.0.0.1' in url:
            QMessageBox.warning(
                self,
                "Cloud URL Not Set",
                "You are still pointing to localhost!\n\n"
                "Close this window and go to:\n"
                "Cloud → Cloud Settings\n\n"
                "Enter your PythonAnywhere URL:\n"
                "http://DinukaNonis.pythonanywhere.com\n\n"
                "Then click Save, and try Login again."
            )
            return False
        return True

    def handle_login(self):
        """Handle login button click."""
        if not self._check_url():
            return

        student_id = self.login_student_id.text().strip()
        password = self.login_password.text()
        
        if not student_id or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        try:
            # Show loading
            self.login_student_id.setEnabled(False)
            self.login_password.setEnabled(False)
            
            # Attempt login
            success = self.api_client.login(student_id, password)
            
            if success:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Welcome back, {self.api_client.user_info.get('name', student_id)}!"
                )
                self.authenticated.emit()
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials")
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Login failed: {str(e)}\n\nMake sure the cloud service is running."
            )
        
        finally:
            self.login_student_id.setEnabled(True)
            self.login_password.setEnabled(True)
    
    def handle_register(self):
        """Handle register button click."""
        if not self._check_url():
            return

        name = self.register_name.text().strip()
        student_id = self.register_student_id.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        # Validation
        if not all([name, student_id, email, password, confirm]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters")
            return
        
        if '@' not in email:
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        try:
            # Show loading
            self.register_name.setEnabled(False)
            self.register_student_id.setEnabled(False)
            self.register_email.setEnabled(False)
            self.register_password.setEnabled(False)
            self.register_confirm.setEnabled(False)
            
            # Attempt registration
            result = self.api_client.register(name, student_id, email, password)
            
            if result.get('success'):
                # Auto-login
                self.api_client.api_key = result.get('api_key')
                self.api_client._save_api_key(self.api_client.api_key)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Account created successfully!\n\nWelcome, {name}!"
                )
                self.authenticated.emit()
                self.accept()
            else:
                error_msg = result.get('error', 'Registration failed')
                QMessageBox.warning(self, "Error", error_msg)
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            error_msg = str(e)
            
            # Parse common errors
            if 'already exists' in error_msg.lower():
                error_msg = "This student ID or email is already registered.\nPlease use the Login tab."
            
            QMessageBox.critical(
                self,
                "Error",
                f"Registration failed: {error_msg}\n\nMake sure the cloud service is running."
            )
        
        finally:
            self.register_name.setEnabled(True)
            self.register_student_id.setEnabled(True)
            self.register_email.setEnabled(True)
            self.register_password.setEnabled(True)
            self.register_confirm.setEnabled(True)
