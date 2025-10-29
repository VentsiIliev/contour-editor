from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QSpinBox,
    QDoubleSpinBox, QSizePolicy
)


class PointItem(QWidget):
    """Individual X,Y point item"""

    pointChanged = pyqtSignal(int, float, float)  # index, x, y
    pointDeleted = pyqtSignal(int)  # index

    def __init__(self, index, x=0.0, y=0.0, parent=None):
        super().__init__(parent)
        self.index = index
        self.init_ui(x, y)

    def init_ui(self, x, y):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)  # Increased padding for touch
        layout.setSpacing(12)  # Increased spacing

        # Point index label - larger for touch
        index_label = QLabel(f"P{self.index:02d}:")
        index_label.setFixedWidth(60)  # Increased from 35
        index_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #905BA9;
                font-size: 16px;
                min-height: 30px;
            }
        """)
        layout.addWidget(index_label)

        # X coordinate - display only
        x_label = QLabel("X:")
        x_label.setFixedWidth(25)  # Increased from 15
        x_label.setStyleSheet("""
            QLabel {
                color: #343a40;
                font-weight: 500;
                font-size: 16px;
                min-height: 30px;
            }
        """)
        layout.addWidget(x_label)

        self.x_display = QLabel(f"{x:.2f}")
        self.x_display.setFixedWidth(120)  # Same width as spinbox was
        self.x_display.setMinimumHeight(50)  # Touch-friendly height
        self.x_display.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 8px 12px;
                color: #343a40;
                font-size: 16px;
                min-height: 50px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.x_display)

        # Y coordinate - display only
        y_label = QLabel("Y:")
        y_label.setFixedWidth(25)  # Increased from 15
        y_label.setStyleSheet("""
            QLabel {
                color: #343a40;
                font-weight: 500;
                font-size: 16px;
                min-height: 30px;
            }
        """)
        layout.addWidget(y_label)

        self.y_display = QLabel(f"{y:.2f}")
        self.y_display.setFixedWidth(120)  # Same width as spinbox was
        self.y_display.setMinimumHeight(50)  # Touch-friendly height
        self.y_display.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 8px 12px;
                color: #343a40;
                font-size: 16px;
                min-height: 50px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.y_display)

        layout.addStretch()

        # Delete button - larger for touch
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(50, 50)  # Increased from 20x20
        delete_btn.clicked.connect(self.delete_point)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                color: #905BA9;
                font-weight: bold;
                font-size: 20px;
                min-width: 50px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #905BA9;
                color: white;
                border-color: #905BA9;
            }
            QPushButton:pressed {
                background-color: #7a4d91;
                border: 3px solid #7a4d91;
            }
        """)
        layout.addWidget(delete_btn)

        self.setStyleSheet("""
            PointItem {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 white, stop: 1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 4px;
                min-height: 70px;
            }
            PointItem:hover {
                border-color: #905BA9;
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 #fefefe, stop: 1 #f5f3f7);
            }
        """)

    def on_value_changed(self):
        """Emit signal when point values change"""
        # This method is no longer needed since values are display-only
        pass

    def delete_point(self):
        """Delete this point"""
        self.pointDeleted.emit(self.index)

    def update_index(self, new_index):
        """Update the point index"""
        self.index = new_index
        # Update the label
        index_label = self.layout().itemAt(0).widget()
        index_label.setText(f"P{self.index:02d}:")

    def get_coordinates(self):
        """Get current X,Y coordinates"""
        try:
            x = float(self.x_display.text())
            y = float(self.y_display.text())
            return x, y
        except ValueError:
            return 0.0, 0.0

    def set_coordinates(self, x, y):
        """Set X,Y coordinates"""
        self.x_display.setText(f"{x:.2f}")
        self.y_display.setText(f"{y:.2f}")

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    point_item = PointItem(1, 10.0, 20.0)
    point_item.show()
    sys.exit(app.exec())