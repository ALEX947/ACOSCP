import sys
from PySide6.QtWidgets import QApplication
from gui.gui import clsGui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = clsGui()
    form.show()
    sys.exit(app.exec())
