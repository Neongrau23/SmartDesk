from PySide6.QtWidgets import QMessageBox


def show_confirmation_dialog(parent, title, message):
    """
    Displays a confirmation dialog with a title and message.
    Returns True if the user clicks "Yes", and False otherwise.
    """
    reply = QMessageBox.question(parent, title, message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
    return reply == QMessageBox.StandardButton.Yes


def show_choice_dialog(parent, title, message, choices):
    """
    Displays a dialog with multiple choices.
    Returns the text of the chosen button, or None if no choice is made.
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    buttons = {}
    for choice in choices:
        button = msg_box.addButton(choice, QMessageBox.ButtonRole.ActionRole)
        buttons[button] = choice

    msg_box.exec()

    clicked_button = msg_box.clickedButton()
    if clicked_button:
        return buttons[clicked_button]
    return None
