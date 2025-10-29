from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from pl_ui.contour_editor.devNewPointManager.devNewPointManager.TouchButton import TouchButton


class ToolbarWidget(QWidget):
    """Toolbar widget with selection and layer controls"""

    # Signals for toolbar actions
    selectAllRequested = pyqtSignal()
    clearSelectionRequested = pyqtSignal()
    expandAllLayersRequested = pyqtSignal()
    collapseAllLayersRequested = pyqtSignal()
    addSegmentRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_label = None
        self.init_ui()
        self.setMinimumHeight(55)  # Increased for touch-friendly sizing
        self.setMaximumHeight(60)  # Adjusted for better proportions
        self.setMinimumWidth(300)  # Minimum width for touch usability

    def init_ui(self):
        """Initialize the toolbar UI"""
        toolbar_layout = QHBoxLayout(self)
        toolbar_layout.setContentsMargins(16, 12, 16, 12)  # Increased for touch
        toolbar_layout.setSpacing(12)  # Increased spacing

        # Selection controls
        select_all_btn = TouchButton("Select All", size=(120, 50))  # Increased height
        select_all_btn.clicked.connect(self.selectAllRequested.emit)
        select_all_btn.setStyleSheet("""
            TouchButton {
                background-color: #905BA9;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #905BA9;
                border-radius: 8px;
                min-width: 120px;
                min-height: 50px;
            }
            TouchButton:hover {
                background-color: #7a4d91;
                border-color: #7a4d91;
            }
            TouchButton:pressed {
                background-color: #6b4280;
                border: 3px solid #6b4280;
            }
        """)
        toolbar_layout.addWidget(select_all_btn)

        clear_btn = TouchButton("Clear", size=(100, 50))  # Increased height
        clear_btn.clicked.connect(self.clearSelectionRequested.emit)
        clear_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                color: #905BA9;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-width: 100px;
                min-height: 50px;
            }
            TouchButton:hover {
                background-color: #905BA9;
                color: white;
                border-color: #905BA9;
            }
            TouchButton:pressed {
                background-color: #7a4d91;
                border: 3px solid #7a4d91;
            }
        """)
        toolbar_layout.addWidget(clear_btn)

        # Layer controls
        expand_all_btn = TouchButton("Expand All", size=(120, 50))  # Increased height
        expand_all_btn.clicked.connect(self.expandAllLayersRequested.emit)
        expand_all_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                color: #905BA9;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-width: 120px;
                min-height: 50px;
            }
            TouchButton:hover {
                background-color: #905BA9;
                color: white;
                border-color: #905BA9;
            }
            TouchButton:pressed {
                background-color: #7a4d91;
                border: 3px solid #7a4d91;
            }
        """)
        toolbar_layout.addWidget(expand_all_btn)

        collapse_all_btn = TouchButton("Collapse All", size=(130, 50))  # Increased height and width
        collapse_all_btn.clicked.connect(self.collapseAllLayersRequested.emit)
        collapse_all_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                color: #905BA9;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-width: 130px;
                min-height: 50px;
            }
            TouchButton:hover {
                background-color: #905BA9;
                color: white;
                border-color: #905BA9;
            }
            TouchButton:pressed {
                background-color: #7a4d91;
                border: 3px solid #7a4d91;
            }
        """)
        toolbar_layout.addWidget(collapse_all_btn)

        # Status label
        self.status_label = QLabel("0 selected")
        self.status_label.setStyleSheet("""
            QLabel {
                font-weight: 600; 
                font-size: 14px;
                color: #343a40; 
                padding: 12px 16px;
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-height: 50px;
                min-width: 160px;
            }
        """)
        toolbar_layout.addWidget(self.status_label)

        # Spacer
        toolbar_layout.addStretch()

        # Add segment button
        add_btn = TouchButton("+ Add Segment", size=(140, 50))  # Increased height and width
        add_btn.clicked.connect(self.addSegmentRequested.emit)
        add_btn.setStyleSheet("""
            TouchButton {
                background-color: #905BA9;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #905BA9;
                border-radius: 8px;
                min-width: 140px;
                min-height: 50px;
            }
            TouchButton:hover {
                background-color: #7a4d91;
                border-color: #7a4d91;
            }
            TouchButton:pressed {
                background-color: #6b4280;
                border: 3px solid #6b4280;
            }
        """)
        toolbar_layout.addWidget(add_btn)

        # Main toolbar styling
        self.setStyleSheet("""
            ToolbarWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 white, stop: 1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 4px;
                min-height: 70px;
            }
        """)

    def update_status(self, selected_count, total_visible):
        """Update the status label"""
        if self.status_label:
            self.status_label.setText(f"{selected_count} selected ({total_visible} visible)")
            if selected_count > 0:
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-weight: bold; 
                        font-size: 14px;
                        color: #905BA9; 
                        padding: 12px 16px;
                        background: #f5f3f7;
                        border: 2px solid #905BA9;
                        border-radius: 8px;
                        min-height: 50px;
                        min-width: 160px;
                    }
                """)
            else:
                self.status_label.setStyleSheet("""
                    QLabel {
                        font-weight: 600; 
                        font-size: 14px;
                        color: #343a40; 
                        padding: 12px 16px;
                        background: white;
                        border: 2px solid #e9ecef;
                        border-radius: 8px;
                        min-height: 50px;
                        min-width: 160px;
                    }
                """)

    def get_status_text(self):
        """Get current status text"""
        return self.status_label.text() if self.status_label else "0 selected"


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QVBoxLayout
    import sys

    app = QApplication(sys.argv)

    # Test widget
    test_widget = QWidget()
    layout = QVBoxLayout(test_widget)

    toolbar = ToolbarWidget()
    layout.addWidget(toolbar)

    # Connect signals for testing
    toolbar.selectAllRequested.connect(lambda: print("Select All clicked"))
    toolbar.clearSelectionRequested.connect(lambda: print("Clear clicked"))
    toolbar.expandAllLayersRequested.connect(lambda: print("Expand All clicked"))
    toolbar.collapseAllLayersRequested.connect(lambda: print("Collapse All clicked"))
    toolbar.addSegmentRequested.connect(lambda: print("Add Segment clicked"))

    # Test status update
    toolbar.update_status(3, 10)

    test_widget.show()
    sys.exit(app.exec())