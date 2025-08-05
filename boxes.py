from PyQt6.QtWidgets import QMessageBox, QWidget

def show_box(code: int, data: str = None, parent: QWidget = None):
    """
    Displays a message box with a specific title, message, and icon based on the provided code and optional data.
    Parameters:
        code (int): The status or error code determining the type of message to display.
        data (str, optional): Additional information or error details to include in the message. Defaults to None.
        parent (QWidget, optional): The parent widget for the message box. Defaults to None.
    Behavior:
        - For specific codes (e.g., 404, 403, 505, 101, 20), displays a tailored message and icon.
        - If `data` is provided, it is included in the message for certain codes.
        - Shows the message box modally with an OK button.
    Returns:
        None
    """
    title = "Progression : "
    msg = ""
    icon = QMessageBox.Icon.Information

    if data is None:
        if code == 404:
            title += "Repository Error"
            msg = "❌ Repository not found or no access (404)"
            icon = QMessageBox.Icon.Warning

        elif code == 403:
            title += "Access Denied"
            msg = "⚠️ Access forbidden (403). Check your token."
            icon = QMessageBox.Icon.Critical

        else:
            title += "Unknown Execution"
            msg = f"❓ Unknown issue (code {code})"
            icon = QMessageBox.Icon.Warning

    else:
        if code == 505:
            title += "GitHub API Error"
            msg = f"📛 GitHub API error:\n\n{data}"
            icon = QMessageBox.Icon.Critical

        elif code == 101:
            title += "Custom Exception"
            msg = f"🛑 An internal error occurred:\n\n{data}"
            icon = QMessageBox.Icon.Critical
        
        elif code == 20 :
            title += "Information"
            msg = f"✔️ Successful Operation : \n\n{data}"
            icon == QMessageBox.Icon.Information
        
        else:
            title += "Unexpected Error"
            msg = f"❔ Unexpected case\n\nCode: {code}\nMessage: {data}"
            icon = QMessageBox.Icon.Warning

    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(msg)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    box.exec()
