import sys
from PySide6.QtWidgets import QApplication
from smartdesk.ui.gui.control_panel import SmartDeskControlPanel

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = SmartDeskControlPanel()
    panel.show()
    sys.exit(app.exec())
