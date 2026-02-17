"""
Cloud settings dialog — with improved connection testing and auto https fix
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QGroupBox,
    QFormLayout, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import logging
import requests

logger = logging.getLogger(__name__)


class CloudSettingsDialog(QDialog):

    def __init__(self, config, api_client, parent=None):
        super().__init__(parent)
        self.config = config
        self.api_client = api_client
        self.setWindowTitle("Cloud Service Settings")
        self.resize(560, 400)
        self.setModal(True)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Cloud Service Configuration")
        f = QFont(); f.setPointSize(15); f.setBold(True)
        title.setFont(f)
        layout.addWidget(title)

        tip = QLabel(
            "💡  Use <b>https://</b> for PythonAnywhere:<br>"
            "<b>https://DinukaNonis.pythonanywhere.com</b>"
        )
        tip.setTextFormat(Qt.RichText)
        tip.setWordWrap(True)
        tip.setStyleSheet(
            "background:#e8f4fd;border:1px solid #bee5eb;"
            "border-radius:6px;padding:10px;font-size:12px;color:#0c5460;"
        )
        layout.addWidget(tip)

        conn_group = QGroupBox("Connection")
        conn_layout = QFormLayout()
        conn_layout.setSpacing(12)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://DinukaNonis.pythonanywhere.com")
        self.url_input.setMinimumHeight(38)
        conn_layout.addRow("Cloud URL:", self.url_input)

        self.test_btn = QPushButton("Test Connection")
        self.test_btn.setMinimumHeight(38)
        self.test_btn.setStyleSheet(
            "QPushButton{background:#0366d6;color:white;border:none;"
            "border-radius:6px;font-weight:600;}"
            "QPushButton:hover{background:#0256c2;}"
            "QPushButton:disabled{background:#aaa;}"
        )
        self.test_btn.clicked.connect(self.test_connection)
        conn_layout.addRow("", self.test_btn)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(60)
        conn_layout.addRow("", self.status_label)

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setMinimumHeight(42)
        save_btn.setStyleSheet(
            "QPushButton{background:#0366d6;color:white;border:none;"
            "border-radius:6px;font-size:14px;font-weight:600;}"
            "QPushButton:hover{background:#0256c2;}"
        )
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(42)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_settings(self):
        url = getattr(self.config, 'cloud_url', '') or ''
        self.url_input.setText(url)

    def _auto_fix_url(self, url: str) -> str:
        """Auto-upgrade http to https for PythonAnywhere."""
        url = url.strip().rstrip('/')
        if 'pythonanywhere.com' in url and url.startswith('http://'):
            url = 'https://' + url[7:]
        return url

    def save_settings(self):
        url = self._auto_fix_url(self.url_input.text())
        self.url_input.setText(url)

        if url and not url.startswith('http'):
            QMessageBox.warning(self, "Invalid URL", "URL must start with https://")
            return

        self.config.save_cloud_settings(bool(url), url)
        if url:
            self.api_client.base_url = url
        QMessageBox.information(self, "Saved", "Settings saved!")
        self.accept()

    def test_connection(self):
        """Test with full diagnosis."""
        url = self._auto_fix_url(self.url_input.text())
        if not url:
            QMessageBox.warning(self, "Error", "Enter a URL first")
            return

        self.url_input.setText(url)  # show fixed url
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing… (up to 25s)")
        self.status_label.setText("⏳ Connecting…")
        self.status_label.setStyleSheet("color:#856404;")
        QApplication.processEvents()

        try:
            resp = requests.get(
                f"{url}/",
                timeout=25,
                allow_redirects=True,
                headers={'User-Agent': 'LabSheetGenerator/3.0'}
            )

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    self.status_label.setText(
                        f"✅  Connected!  "
                        f"Status: {data.get('status','running')}  "
                        f"· Users: {data.get('users', 0)}"
                    )
                    self.status_label.setStyleSheet(
                        "color:#155724;background:#d4edda;"
                        "padding:8px;border-radius:4px;font-weight:600;"
                    )
                except Exception:
                    self.status_label.setText("✅  Connected!")
                    self.status_label.setStyleSheet(
                        "color:#155724;font-weight:600;"
                    )

            else:
                self.status_label.setText(
                    f"⚠️  Server replied: HTTP {resp.status_code}\n"
                    f"Check PythonAnywhere → Web → Error log"
                )
                self.status_label.setStyleSheet("color:#856404;")

        except requests.exceptions.SSLError:
            # Try http fallback
            try:
                http_url = url.replace('https://', 'http://')
                resp2 = requests.get(f"{http_url}/", timeout=15, allow_redirects=True)
                if resp2.status_code == 200:
                    self.url_input.setText(http_url)
                    self.status_label.setText(
                        "✅  Connected via http://  (URL updated)"
                    )
                    self.status_label.setStyleSheet(
                        "color:#155724;font-weight:600;"
                    )
                else:
                    self.status_label.setText("⚠️  SSL error. Try http:// instead.")
                    self.status_label.setStyleSheet("color:#856404;")
            except Exception:
                self.status_label.setText("❌  SSL error and http fallback also failed.")
                self.status_label.setStyleSheet("color:#721c24;")

        except requests.exceptions.ConnectionError:
            self.status_label.setText(
                "❌  Cannot reach the server.\n"
                "• Check the URL is exactly right\n"
                "• Open PythonAnywhere → Web tab → click Reload\n"
                "• Make sure virtualenv path is set"
            )
            self.status_label.setStyleSheet("color:#721c24;")

        except requests.exceptions.Timeout:
            self.status_label.setText(
                "⏱  Timed out (25s).\n"
                "PythonAnywhere free apps can be slow to start.\n"
                "Click Save and try Register — it may still work."
            )
            self.status_label.setStyleSheet("color:#856404;")

        except Exception as e:
            self.status_label.setText(f"❌  {str(e)[:140]}")
            self.status_label.setStyleSheet("color:#721c24;")

        finally:
            self.test_btn.setEnabled(True)
            self.test_btn.setText("Test Connection")
