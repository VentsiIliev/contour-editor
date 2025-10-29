from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel
)

from pl_ui.contour_editor.devNewPointManager.devNewPointManager.TouchButton import TouchButton


class SimpleSegmentItem(QWidget):
    """Simplified segment widget without complex drag interactions - Touch-friendly design"""

    selectionChanged = pyqtSignal(int, bool)
    segmentDeleted = pyqtSignal(int)
    toggleSegmentRequested = pyqtSignal(str, bool)  # layer_name, is_expanded
    segmentVisibilityToggled = pyqtSignal(int, bool)  # seg_index, is_visible
    settingsRequested = pyqtSignal(int)  # seg_index

    def __init__(self, seg_index, layer_name="Contour", parent=None):
        super().__init__(parent)
        self.seg_index = seg_index
        self.layer_name = layer_name
        self.is_selected = False
        self.is_expanded = True

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)  # Increased padding for touch
        layout.setSpacing(12)  # Increased spacing

        # Drag handle indicator - larger for touch
        drag_label = QLabel("⋮⋮")
        drag_label.setFixedSize(40, 50)  # Increased from 20x30
        drag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drag_label.setStyleSheet("""
            QLabel {
                color: #905BA9;
                font-weight: bold;
                font-size: 18px;
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
            }
        """)
        layout.addWidget(drag_label)

        # Toggle button - larger for touch
        self.toggle_btn = TouchButton("▼", size=(50, 50))  # Increased from 30x30
        self.toggle_btn.clicked.connect(self.toggle_expansion)
        self.toggle_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                color: #905BA9;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-width: 50px;
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
        layout.addWidget(self.toggle_btn)

        # Segment info - larger text for touch
        self.info_label = QLabel(f"S{self.seg_index:02d} - {self.layer_name}")
        self.info_label.setStyleSheet("""
            QLabel {
                font-weight: 600;
                font-size: 16px;
                color: #343a40;
                padding: 8px 12px;
                background: white;
                border-radius: 8px;
                border: 2px solid #e9ecef;
                min-width: 80px;
                max-width: 140px;
                min-height: 30px;
            }
        """)
        layout.addWidget(self.info_label, 1)

        # settings button - larger for touch
        settings_btn = TouchButton("⚙️", size=(50, 50))  # Increased from 30x30
        settings_btn.setToolTip("Segment settings")
        settings_btn.clicked.connect(self.on_settings_clicked)
        settings_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                color: #905BA9;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-width: 50px;
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
        layout.addWidget(settings_btn)

        # visibility toggle button - larger for touch
        self.visibility_btn = TouchButton("👁️", size=(50, 50))  # Increased from 30x30
        self.visibility_btn.setToolTip("Toggle visibility")
        self.visibility_btn.clicked.connect(self.toggleVisibility)
        self.visibility_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                color: #905BA9;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-width: 50px;
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
        layout.addWidget(self.visibility_btn)

        # Selection indicator - larger for touch
        self.select_btn = TouchButton("☐", size=(50, 50))  # Increased from 30x30
        self.select_btn.clicked.connect(self.toggle_selection)
        self.select_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                color: #905BA9;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                min-width: 50px;
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
        layout.addWidget(self.select_btn)

        # Delete button - larger for touch
        delete_btn = TouchButton("×", size=(50, 50))  # Increased from 30x30
        delete_btn.clicked.connect(lambda: self.segmentDeleted.emit(self.seg_index))
        delete_btn.setStyleSheet("""
            TouchButton {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                color: #905BA9;
                font-weight: bold;
                font-size: 20px;
                min-width: 50px;
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
        layout.addWidget(delete_btn)

        self.update_style()

    def on_settings_clicked(self):
        """Emit signal to request segment settings"""
        self.settingsRequested.emit(self.seg_index)

    def toggleVisibility(self):
        """Toggle visibility of the segment"""
        self.is_visible = not getattr(self, 'is_visible', True)
        self.visibility_btn.setText("👁️" if self.is_visible else "👁️‍🗨️")
        self.segmentVisibilityToggled.emit(self.seg_index, self.is_visible)

    def toggle_selection(self):
        self.is_selected = not self.is_selected
        self.update_style()
        self.selectionChanged.emit(self.seg_index, self.is_selected)

    def set_selected(self, selected):
        if self.is_selected != selected:
            self.is_selected = selected
            self.update_style()

    def update_info_label(self):
        """Update the info label text and trigger repaint"""
        self.info_label.setText(f"S{self.seg_index:02d} - {self.layer_name}")
        self.info_label.update()

        # Also update the widget itself
        self.update()

    def toggle_expansion(self):
        """Toggle the expansion state"""
        self.is_expanded = not self.is_expanded
        self.update_toggle_button()
        self.toggleSegmentRequested.emit(self.layer_name, self.is_expanded)

    def update_toggle_button(self):
        """Update the toggle button appearance"""
        if self.is_expanded:
            self.toggle_btn.setText("▼")
            self.toggle_btn.setToolTip("Collapse layer")
        else:
            self.toggle_btn.setText("▶")
            self.toggle_btn.setToolTip("Expand layer")

    def update_style(self):
        """Update visual state based on selection"""
        if self.is_selected:
            self.select_btn.setText("☑")
            self.select_btn.setStyleSheet("""
                TouchButton {
                    background-color: #905BA9;
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border: 2px solid #905BA9;
                    border-radius: 8px;
                    min-width: 50px;
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
            self.setStyleSheet("""
                SimpleSegmentItem {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #fefefe, stop: 1 #f5f3f7);
                    border: 3px solid #905BA9;
                    border-radius: 12px;
                    margin: 4px;
                    min-height: 70px;
                }
            """)
        else:
            self.select_btn.setText("☐")
            self.select_btn.setStyleSheet("""
                TouchButton {
                    background-color: #f8f9fa;
                    color: #905BA9;
                    font-size: 18px;
                    font-weight: bold;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    min-width: 50px;
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
            self.setStyleSheet("""
                SimpleSegmentItem {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 white, stop: 1 #f8f9fa);
                    border: 2px solid #e9ecef;
                    border-radius: 12px;
                    margin: 4px;
                    min-height: 70px;
                }
                SimpleSegmentItem:hover {
                    border-color: #905BA9;
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #fefefe, stop: 1 #f5f3f7);
                }
            """)

        # Force visual update
        self.update()
        self.repaint()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = SimpleSegmentItem(seg_index=1, layer_name="Test Layer")
    widget.show()
    sys.exit(app.exec())