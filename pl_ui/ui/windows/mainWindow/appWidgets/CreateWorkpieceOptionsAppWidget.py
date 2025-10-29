from PyQt6.QtCore import pyqtSignal

import os

from pl_ui.ui.widgets.WorkpieceOptionsWidget import WorkpieceOptionsWidget
from pl_ui.ui.windows.mainWindow.appWidgets.AppWidget import AppWidget


class CreateWorkpieceOptionsAppWidget(AppWidget):
    """Specialized widget for User Management application"""
    create_workpiece_camera_selected = pyqtSignal()
    create_workpiece_dxf_selected = pyqtSignal()
    def __init__(self, parent=None,controller=None):
        self.controller = controller
        super().__init__("Create Workpiece Options", parent)
    def setup_ui(self):
        """Setup the user management specific UI"""
        super().setup_ui()  # Get the basic layout with back button

        # Replace the content with actual UserManagementWidget if available
        try:
            # Remove the placeholder content
            content_widget = WorkpieceOptionsWidget(controller=self.controller)
            content_widget.create_workpiece_camera_selected.connect(self.camera_selected)
            content_widget.create_workpiece_dxf_selected.connect(self.dxf_selected)
            # Replace the last widget in the layout (the placeholder) with the real widget
            layout = self.layout()
            old_content = layout.itemAt(layout.count() - 1).widget()
            layout.removeWidget(old_content)
            old_content.deleteLater()

            # Set margins to center (adjust values as needed)
            layout.setContentsMargins(50, 20, 50, 20)  # left, top, right, bottom
            layout.addWidget(content_widget)
            print("Create Workpiece Options widget loaded successfully")
        except ImportError:
            import traceback
            traceback.print_exc()
            # Keep the placeholder if the UserManagementWidget is not available
            print("Create Workpiece not available, using placeholder")


    def camera_selected(self):
        """Handle camera selection"""
        print("Camera selected signal emitted")
        self.create_workpiece_camera_selected.emit()

    def dxf_selected(self):
        """Handle DXF selection"""
        print("DXF selected signal emitted")
        self.create_workpiece_dxf_selected.emit()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = CreateWorkpieceOptionsAppWidget()
    widget.resize(600, 400)
    widget.show()
    sys.exit(app.exec())