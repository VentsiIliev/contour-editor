from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem


class WorkingDragList(QListWidget):
    """Minimal list widget that should work with drag and drop"""

    segmentMoved = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Enable basic drag and drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        # Store original order for comparison
        self.item_order = []

        self.setStyleSheet("""
            WorkingDragList {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background-color: #ffffff;
                alternate-background-color: #f9fafb;
            }
        """)

    def add_segment_item(self, widget, seg_index):
        """Add a segment item that can be dragged"""
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, {
            'type': 'segment',
            'seg_index': seg_index,
            'layer_name': widget.layer_name
        })
        item.setFlags(Qt.ItemFlag.ItemIsEnabled |
                      Qt.ItemFlag.ItemIsSelectable |
                      Qt.ItemFlag.ItemIsDragEnabled)

        self.addItem(item)
        self.setItemWidget(item, widget)
        self.item_order.append(('segment', seg_index))
        return item

    def add_layer_header(self, widget):
        """Add a layer header that cannot be dragged"""
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.ItemDataRole.UserRole, {
            'type': 'layer',
            'layer_name': widget.layer_name
        })
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Not draggable

        self.addItem(item)
        self.setItemWidget(item, widget)
        self.item_order.append(('layer', None))
        return item

    def hide_layer_segments(self, layer_name):
        """Hide all segments belonging to a specific layer"""
        for i in range(self.count()):
            item = self.item(i)
            if item:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data and data.get('type') == 'segment' and data.get('layer_name') == layer_name:
                    item.setHidden(True)

    def show_layer_segments(self, layer_name):
        """Show all segments belonging to a specific layer"""
        for i in range(self.count()):
            item = self.item(i)
            if item:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data and data.get('type') == 'segment' and data.get('layer_name') == layer_name:
                    item.setHidden(False)

    def dropEvent(self, event):
        """Override drop to emit signal"""
        # Store the current item being dropped
        dropping_item = self.currentItem()
        if dropping_item:
            data = dropping_item.data(Qt.ItemDataRole.UserRole)
            if data and data.get('type') == 'segment':
                old_row = self.row(dropping_item)
                seg_index = data.get('seg_index')

                # Perform the drop
                super().dropEvent(event)

                # Get new position
                new_row = self.row(dropping_item)

                if old_row != new_row:
                    print(f"🔄 Segment {seg_index} moved from {old_row} to {new_row}")
                    self.segmentMoved.emit(seg_index, new_row)
                return

        super().dropEvent(event)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = WorkingDragList()
    widget.show()
    sys.exit(app.exec())