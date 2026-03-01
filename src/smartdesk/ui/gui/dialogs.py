import subprocess
import sys
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtCore import Qt


def show_confirmation_dialog(parent, title, message):
    """
    Displays a confirmation dialog with a title and message.
    Returns True if the user clicks "Yes", and False otherwise.
    """
    app = QApplication.instance()
    if app is None:
        # Background thread/process mode: spawn a subprocess to avoid Qt thread crashes
        script = f"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

app = QApplication([])
msg_box = QMessageBox()
msg_box.setWindowTitle({repr(title)})
msg_box.setText({repr(message)})
msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
msg_box.setDefaultButton(QMessageBox.StandardButton.No)
msg_box.setWindowFlag(Qt.WindowStaysOnTopHint)

reply = msg_box.exec()
if reply == QMessageBox.StandardButton.Yes:
    print("YES")
else:
    print("NO")
"""
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return result.stdout.strip() == "YES"

    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
    if parent is None:
        msg_box.setWindowFlag(Qt.WindowStaysOnTopHint)

    reply = msg_box.exec()
    return reply == QMessageBox.StandardButton.Yes


def show_choice_dialog(parent, title, message, choices):
    """
    Displays a dialog with multiple choices.
    Returns the text of the chosen button, or None if no choice is made.
    """
    app = QApplication.instance()
    if app is None:
        # Background thread/process mode: spawn a subprocess to avoid Qt thread crashes
        script = f"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

app = QApplication([])
msg_box = QMessageBox()
msg_box.setWindowTitle({repr(title)})
msg_box.setText({repr(message)})
msg_box.setWindowFlag(Qt.WindowStaysOnTopHint)

choices = {repr(choices)}
buttons = {{}}
for choice in choices:
    btn = msg_box.addButton(choice, QMessageBox.ButtonRole.ActionRole)
    buttons[btn] = choice

msg_box.exec()
clicked_button = msg_box.clickedButton()
if clicked_button:
    print(buttons[clicked_button])
"""
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        output = result.stdout.strip()
        if output in choices:
            return output
        return None

    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    if parent is None:
        msg_box.setWindowFlag(Qt.WindowStaysOnTopHint)

    buttons = {}
    for choice in choices:
        button = msg_box.addButton(choice, QMessageBox.ButtonRole.ActionRole)
        buttons[button] = choice

    msg_box.exec()

    clicked_button = msg_box.clickedButton()
    if clicked_button:
        return buttons[clicked_button]
    return None
