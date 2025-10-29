import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout
)

from pl_ui.contour_editor.devNewPointManager.devNewPointManager.SegmentManager import SegmentManager


class TestApp(QWidget):
    """Test application"""

    def __init__(self):
        super().__init__(parent=None)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Collapsible Layer Segment Manager")
        self.setGeometry(200, 200, 400, 700)
        # self.setFixedWidth(700)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        manager = SegmentManager()
        layout.addWidget(manager)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set a clean font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Create and show the test app
    test_app = TestApp()
    test_app.show()

    print("🚀 Collapsible Layer Segment Manager Started")
    print("Click the ▼/▶ buttons to collapse/expand layers!")

    sys.exit(app.exec())