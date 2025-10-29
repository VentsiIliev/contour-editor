from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMainWindow,
    QApplication, QLabel, QSplitter
)

# Import your custom widgets
from pl_ui.contour_editor.TopbarWidget import TopBarWidget
from SegmentManager import SegmentManager
from ToolbarWidget import ToolbarWidget
from pl_ui.contour_editor.ContourEditor import ContourEditor


class MainWindow(QMainWindow):
    """Main application window with TopBar and SegmentManager"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize the main window UI"""
        self.setWindowTitle("Contour Editor - Touch Interface")
        self.setMinimumSize(1200, 800)  # Touch-friendly minimum size

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)  # Touch-friendly margins
        main_layout.setSpacing(12)

        # Create TopBar at the top
        self.top_bar = TopBarWidget()
        main_layout.addWidget(self.top_bar)

        # Create horizontal splitter for main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)  # Prevent panels from fully collapsing

        # Create main content area (placeholder for contour editor)
        self.main_content = QWidget()
        self.main_content.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 white, stop: 1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 4px;
            }
        """)

        # Add placeholder content to main area
        main_content_layout = QVBoxLayout(self.main_content)
        main_content_layout.setContentsMargins(20, 20, 20, 20)

        # placeholder_label = QLabel("Contour Editor Area")
        self.contour_editor = ContourEditor(visionSystem=None)
        self.contour_editor.addPointRequested.connect(self.onAddPointRequested)
        # placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contour_editor.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #905BA9;
                background: none;
                border: 2px dashed #905BA9;
                border-radius: 8px;
                padding: 40px;
                min-height: 200px;
            }
        """)
        main_content_layout.addWidget(self.contour_editor)

        # Create SegmentManager for the right panel
        self.segment_manager = SegmentManager()
        self.segment_manager.setMinimumWidth(400)  # Touch-friendly minimum width
        self.segment_manager.setMaximumWidth(600)  # Prevent it from getting too wide
        self.segment_manager.toggleToolbarRequested.connect(self.toggle_toolbar)
        self.segment_manager.addSegmentRequested.connect(lambda layer:self.onAddSegmentRequested(layer))
        self.segment_manager.layerVisibilityToggled.connect(lambda layer_name, visible, onSuccess, onFailure: self.toggleLayerVisibility(layer_name, visible, onSuccess, onFailure))
        self.segment_manager.segmentVisibilityToggled.connect(self.contour_editor.set_segment_visibility)
        self.segment_manager.selectedSegmentChanged.connect(lambda seg_index: self.contour_editor.set_active_segment(seg_index))
        self.segment_manager.layerLockRequested.connect(lambda layer_name,locked,onSuccess,onFailure: self.contour_editor.set_layer_locked(layer_name,locked,onSuccess,onFailure))
        self.segment_manager.addSegmentRequested.connect(lambda layer_name,onSuccess,onFailure: self.contour_editor.addNewSegment(layer_name,onSuccess,onFailure))
        # Add widgets to splitter
        content_splitter.addWidget(self.main_content)
        content_splitter.addWidget(self.segment_manager)

        # Set initial splitter sizes (70% main content, 30% segment manager)
        content_splitter.setSizes([800, 400])

        # Style the splitter handle for touch-friendly resizing
        content_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #905BA9;
                width: 8px;
                border-radius: 4px;
                margin: 4px 0px;
            }
            QSplitter::handle:hover {
                background-color: #7a4d91;
            }
            QSplitter::handle:pressed {
                background-color: #6b4280;
            }
        """)

        # Add splitter to main layout
        main_layout.addWidget(content_splitter)
        self.toolBar = self.segment_manager.toolbar
        main_layout.addWidget(self.toolBar)
        # Set main window styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f9fafb;
            }
        """)

    def toggleLayerVisibility(self, layer_id,visible,onSuccess, onFailure):
        """Toggle visibility of a specific layer in the segment manager"""
        print(f"Toggling visibility for layer {layer_id}")
        result = self.contour_editor.set_layer_visibility(layer_id,visible)

        if result:
            print(f"Layer {layer_id} visibility set to {visible}")
            onSuccess()
        else:
            print(f"Failed to set visibility for layer {layer_id}")
            onFailure()
    def onAddPointRequested(self, point):
        """Handle add point request from ContourEditor"""
        print("Add Point Request received: ", point)
        self.segment_manager.add_point(point)
        return True

    def onAddSegmentRequested(self,layer):
        print("Add Segment Request received")
        self.contour_editor.addNewSegment(layer)
        return True

    def toggle_toolbar(self):
        """Toggle visibility of the toolbar"""

        if self.toolBar.isVisible():
            self.toolBar.hide()
        else:
            self.toolBar.show()

    def get_top_bar(self):
        """Get reference to the top bar widget"""
        return self.top_bar

    def get_segment_manager(self):
        """Get reference to the segment manager widget"""
        return self.segment_manager

    def set_main_content_widget(self, widget):
        """Replace the placeholder with actual contour editor widget"""
        # Remove the current main content
        content_splitter = self.centralWidget().layout().itemAt(1).widget()

        # Replace the main content widget
        old_main_content = content_splitter.widget(0)
        old_main_content.setParent(None)

        # Style the new widget to match
        widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 white, stop: 1 #f8f9fa);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 4px;
            }
        """)

        content_splitter.insertWidget(0, widget)
        self.main_content = widget


class DemoApplication(QWidget):
    """Demo application showing the complete interface"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize demo UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create main window
        self.main_window = MainWindow()

        # You can access components like this:
        top_bar = self.main_window.get_top_bar()
        segment_manager = self.main_window.get_segment_manager()

        # Example of connecting signals (customize as needed)
        # top_bar.some_signal.connect(segment_manager.some_slot)

        # Show the main window
        self.main_window.show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Create and show the main window directly
    window = MainWindow()
    window.show()

    # Or use the demo application wrapper
    # demo = DemoApplication()

    sys.exit(app.exec())
