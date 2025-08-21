import os
import sys
import configparser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QLineEdit, QCheckBox, QTextEdit, QGraphicsDropShadowEffect,
    QMessageBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QColor, QIcon

from github_edit import Master

# Status dictionary for status selection
status_dict = {
    "under_dev": "🔴 In Development",
    "ready_soon": "🟠 Almost Ready",
    "finished": "🟢 Completed",
    "under_update": "🔘 Updating"
}

class NeonApp(QWidget):
    """
    NeonApp is a QWidget-based PyQt application for updating a user's GitHub README.md status.
    Features:
        - Modern neon-themed UI with custom styles and drop shadows.
        - Input fields for GitHub username, personal access token, repository, and status selection.
        - Option to set repository visibility (public/private).
        - Credential management: save, load, and reset user credentials securely in a config file.
        - "Apply Changes" and "Approve" workflow for confirming and executing status updates.
        - Displays a summary and status messages in a read-only QTextEdit.
        - Integrates with a Master class to perform the actual GitHub update operation.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Progression")
        self.setMinimumSize(900, 600)
        self.resize(950, 650)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)  # Window is resizable

        self.setWindowIcon(QIcon("data/main-app.ico"))

        # Set neon-themed stylesheet
        self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0a0a0f, stop:1 #001f24);
                color: #00fff7;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLabel#titleLabel {
                font-weight: 900;
                font-size: 26px;
                margin-bottom: 25px;
                letter-spacing: 2px;
                color: #00fff7;
                text-shadow: 0 0 10px #00fff7;
            }
            QLineEdit, QComboBox, QTextEdit {
                border-radius: 12px;
                padding: 12px;
                font-size: 16px;
                background-color: #001f24;
                color: #00fff7;
                border: 2px solid #00fff7;
                selection-background-color: #00fff7;
                selection-color: #001f24;
                letter-spacing: 0.5px;
            }
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 16px;
                padding: 20px;
                background-color: #00262b;
                border-radius: 12px;
                color: #00fff7;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #0a0a0f, stop:1 #001f24);
        
                background-color: #00fff7;
                border: none;
                border-radius: 14px;
                padding: 14px;
                font-weight: 900;
                font-size: 17px;
                color: #001f24;
                letter-spacing: 1.5px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #00fff7;
            }
            QPushButton:pressed {
                background-color: #00c8cc;
            }
            QPushButton:disabled {
                background-color: #005055;
                color: #00373b;
            }
            QCheckBox {
                font-size: 16px;
                font-weight: 700;
                color: #00fff7;
            }
            QCheckBox::indicator {
                width: 26px;
                height: 26px;
                border-radius: 13px;
                background: #001f24;
                border: 2.5px solid #00fff7;
            }
            QCheckBox::indicator:checked {
                background: #00fff7;
                border: 2.5px solid #00fff7;
            }
        """)

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        self.setLayout(main_layout)

        # Title label
        self.title = QLabel("Update your README.md status")
        self.title.setObjectName("titleLabel")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title)

        # Horizontal layout for two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(40)
        main_layout.addLayout(content_layout)

        # Left column: user info and reset button
        left_col = QVBoxLayout()
        left_col.setSpacing(20)
        content_layout.addLayout(left_col, 1)  # ratio 1

        # GitHub username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("GitHub Username")
        self.username_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        left_col.addWidget(self.username_input)

        # GitHub token input
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Access Token")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        left_col.addWidget(self.token_input)

        # Reset credentials button
        self.reset_btn = QPushButton("Reset Credentials")
        self.reset_btn.clicked.connect(self.reset_credentials)
        left_col.addWidget(self.reset_btn)

        # Spacer to push content to top
        left_col.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Right column: repo, status, visibility, buttons, summary
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        content_layout.addLayout(right_col, 2)  # ratio 2, wider

        # Repository input
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("repo-name")
        self.repo_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        right_col.addWidget(self.repo_input)

        # Status selection combo box
        self.status_combo = QComboBox()
        for key, val in status_dict.items():
            self.status_combo.addItem(val, userData=key)
        right_col.addWidget(self.status_combo)

        # Public/private checkbox
        self.public_check = QCheckBox("🌐 Public")
        self.public_check.setChecked(True)
        right_col.addWidget(self.public_check)

        # Buttons layout (Apply and Approve)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        right_col.addLayout(btn_layout)

        # Apply changes button
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_changes)
        btn_layout.addWidget(self.apply_btn)

        # Approve button (hidden by default)
        self.approve_btn = QPushButton("✅ Approve")
        self.approve_btn.clicked.connect(self.approve_changes)
        self.approve_btn.hide()
        btn_layout.addWidget(self.approve_btn)

        # Special style for approve_btn (neon green)
        self.approve_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff99;
                border: none;
                border-radius: 14px;
                padding: 14px;
                font-weight: 900;
                font-size: 17px;
                color: #001f24;
                letter-spacing: 1.5px;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #00e68a;
            }
            QPushButton:pressed {
                background-color: #00cc75;
            }
            QPushButton:disabled {
                background-color: #004d2e;
                color: #00994d;
            }
        """)

        # Neon shadow effect for buttons
        shadow_btn = QGraphicsDropShadowEffect()
        shadow_btn.setBlurRadius(25)
        shadow_btn.setColor(QColor(0, 255, 153, 180))  # neon green shadow
        shadow_btn.setOffset(0, 0)
        self.apply_btn.setGraphicsEffect(shadow_btn)
        self.approve_btn.setGraphicsEffect(shadow_btn)


        # Output summary text area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.hide()
        self.output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        right_col.addWidget(self.output)

        # Neon shadow effect for output text
        shadow_text = QGraphicsDropShadowEffect()
        shadow_text.setBlurRadius(30)
        shadow_text.setColor(QColor(0, 255, 255, 150))  # neon cyan shadow
        shadow_text.setOffset(0, 0)
        self.output.setGraphicsEffect(shadow_text)


        # Config file paths
        self.config_dir = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "GitHubProgression")
        self.config_file = os.path.join(self.config_dir, "config.ini")

        # Load config on startup
        self.load_config()

        # Fade-in animation for window
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(800)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.start()

    def load_config(self):
        # Load user credentials from config file
        if not os.path.exists(self.config_file):
            self.set_inputs_enabled(True)
            return
        config = configparser.ConfigParser()
        config.read(self.config_file)
        if "USER" in config:
            username = config["USER"].get("username", "")
            token = config["USER"].get("token", "")
            if username and token:
                self.username_input.setText(username)
                self.token_input.setText(token)
                self.username_input.setReadOnly(True)
                self.token_input.setReadOnly(True)
                self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)
                self.apply_btn.setEnabled(True)
                self.reset_btn.setEnabled(True)
                self.approve_btn.hide()
                self.output.hide()
                self.set_inputs_enabled(True)
            else:
                self.set_inputs_enabled(True)
        else:
            self.set_inputs_enabled(True)

    def save_config(self, username, token):
        # Save user credentials to config file
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
        config = configparser.ConfigParser()
        config["USER"] = {"username": username, "token": token}
        with open(self.config_file, "w") as f:
            config.write(f)

    def reset_credentials(self):
        # Reset credentials and clear input fields
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.username_input.clear()
        self.token_input.clear()
        self.username_input.setReadOnly(False)
        self.token_input.setReadOnly(False)
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.apply_btn.setEnabled(True)
        self.output.hide()
        self.approve_btn.hide()
        self.set_inputs_enabled(True)

    def apply_changes(self):
        # Prepare summary and enable approval
        self.username = self.username_input.text() or "UnknownUser"
        self.token = self.token_input.text()
        self.repo = self.repo_input.text() or "Unnamed"
        self.status_key = self.status_combo.currentData()
        self.emoji_status = status_dict.get(self.status_key, "❔ Unknown")
        self.visibility = "🌐 Public" if self.public_check.isChecked() else "🔒 Private"

        if not self.token:
            QMessageBox.warning(self, "Missing Token", "Please enter your GitHub Personal Access Token.")
            return

        self.save_config(self.username, self.token)

        self.username_input.setReadOnly(True)
        self.token_input.setReadOnly(True)
        self.token_input.setEchoMode(QLineEdit.EchoMode.Normal)

        self.summary_text = (
            f"↪ User: {self.username}\n"
            f"↪ Status: {self.emoji_status}\n"
            f"↪ Repository: {self.repo}\n"
            f"↪ Visibility: {self.visibility}\n"
            "(Token is saved securely)"
        )
        self.output.setText("Approve these changes?\n\n" + self.summary_text)
        self.output.show()
        self.approve_btn.show()
        self.approve_btn.setEnabled(True)

        self.set_inputs_enabled(True)  # Inputs remain enabled after apply

    def approve_changes(self):
        # Execute the GitHub update operation
        self.output.setText("🚀 Launching procedure...\n\n" + self.summary_text)
        self.approve_btn.setEnabled(False)
        self.apply_btn.setEnabled(False)
        self.set_inputs_enabled(False)

        # Clean and extract input values
        username = self.username_input.text().strip() or "UnknownUser"
        token = self.token_input.text().strip()
        repo_text = self.repo_input.text().strip() or "Unnamed"

        # If repo input contains username/repo, split it
        if "/" in repo_text:
            parts = repo_text.split("/")
            username = parts[0]
            repo = parts[1]
        else:
            repo = repo_text

        status_key = self.status_combo.currentData()
        visibility = "🌐 Public" if self.public_check.isChecked() else "🔒 Private"

        data_tuple = (username, token, repo, status_key, visibility)


        Call = Master(data_tuple)
        Call.GitEdit()

        QTimer.singleShot(2000, self.show_done_message)

    def set_inputs_enabled(self, enabled: bool):
        # Enable or disable input fields and buttons
        self.username_input.setEnabled(enabled and not self.username_input.isReadOnly())
        self.token_input.setEnabled(enabled and not self.token_input.isReadOnly())
        self.repo_input.setEnabled(enabled)
        self.status_combo.setEnabled(enabled)
        self.public_check.setEnabled(enabled)
        if enabled:
            self.apply_btn.setEnabled(True)

    def show_done_message(self):
        # Show completion message after update
        self.output.setText("✅ All done!\nNow You Can Close That Window")
        self.approve_btn.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeonApp()
    window.show()
    sys.exit(app.exec())