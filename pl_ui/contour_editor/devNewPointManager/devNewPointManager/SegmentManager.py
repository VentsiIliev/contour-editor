from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel
)

from pl_ui.contour_editor.devNewPointManager.devNewPointManager.LayerHeaderItem import LayerHeaderItem
from pl_ui.contour_editor.devNewPointManager.devNewPointManager.SimpleSegmentItem import SimpleSegmentItem
from pl_ui.contour_editor.devNewPointManager.devNewPointManager.TouchButton import TouchButton
from pl_ui.contour_editor.devNewPointManager.devNewPointManager.WorkingDragList import WorkingDragList
from pl_ui.contour_editor.devNewPointManager.devNewPointManager.PointItem import PointItem
from pl_ui.contour_editor.devNewPointManager.devNewPointManager.ToolbarWidget import ToolbarWidget
from pl_ui.ui.widgets.ToastWidget import ToastWidget

class SegmentManager(QWidget):
    """Main segment management widget"""
    toggleToolbarRequested = pyqtSignal()  # Signal to toggle toolbar visibility

    addSegmentRequested = pyqtSignal(str,object,object)  # Signal to add a new segment
    layerVisibilityToggled = pyqtSignal(str, bool)  # layer_name, is_visible
    layerLockRequested = pyqtSignal(str, bool,object,object)  # layer_name, is_locked
    segmentVisibilityToggled = pyqtSignal(int, bool)  # segment_name, is_visible
    selectedSegmentChanged = pyqtSignal(int, bool)  # seg_index, selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []
        self.selected_segments = set()
        self.layer_headers = {}  # Store layer headers by name
        self.layer_expanded_state = {}  # Track expansion state
        self.layer_segments = {}  # Track segments per layer: {layer_name: [segments]}
        self.layer_segment_counters =-1   # Track next segment ID per layer
        self.init_ui()
        self.populate_demo_data()
        self.selected_layer = None  # Track currently selected layer

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Collapsible Layer Segment Manager")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
                padding: 16px;
                background-color: #f8f9fa;
                border-radius: 8px;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(title)

        # Instructions
        instructions = QLabel("""
        🎯 Features:
        • Click ▼/▶ buttons to collapse/expand layers
        • Drag segments to reorder (only visible segments)
        • Layer headers cannot be moved
        • Each layer has independent segment numbering (starts from 0)
        • Check console for events
        """)
        instructions.setStyleSheet("""
            QLabel {
                background-color: #dbeafe;
                border: 1px solid #3b82f6;
                border-radius: 6px;
                padding: 12px;
                color: #1e40af;
            }
        """)
        # layout.addWidget(instructions)

        # Create main content container with overlay support
        self.main_container = QWidget()
        main_container_layout = QVBoxLayout(self.main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)

        # Create the list
        self.segment_list = WorkingDragList()
        self.segment_list.segmentMoved.connect(self.on_segment_moved)

        main_container_layout.addWidget(self.segment_list)

        # Create and configure toolbar (initially hidden)
        self.toolbar = ToolbarWidget()
        self.toolbar.selectAllRequested.connect(self.select_all)
        self.toolbar.clearSelectionRequested.connect(self.clear_selection)
        self.toolbar.expandAllLayersRequested.connect(self.expand_all_layers)
        self.toolbar.collapseAllLayersRequested.connect(self.collapse_all_layers)
        # self.toolbar.addSegmentRequested.connect(self.add_segment)
        self.toolbar.setVisible(False)  # Initially hidden
        # main_container_layout.addWidget(self.toolbar)

        # Add main container to layout
        layout.addWidget(self.main_container)

        # Create floating toggle button
        self.toggle_button = TouchButton("🔧", size=(60, 60))  # Tools icon
        self.toggle_button.setParent(self.main_container)
        self.toggle_button.clicked.connect(self.on_toggle_toolbar)
        self.toggle_button.setStyleSheet("""
            TouchButton {
                background: qradient(cx: 0.5, cy: 0.5, radius: 0.5,
                                   stop: 0 #905BA9, stop: 1 #7a4d91);
                color: white;
                font-weight: bold;
                font-size: 24px;
                border: 3px solid white;
                border-radius: 30px;
                min-width: 60px;
                min-height: 60px;
            }
            TouchButton:hover {
                background: qradient(cx: 0.5, cy: 0.5, radius: 0.5,
                                   stop: 0 #7a4d91, stop: 1 #6b4280);
                border-color: #f8f9fa;
            }
            TouchButton:pressed {
                background: qradient(cx: 0.5, cy: 0.5, radius: 0.5,
                                   stop: 0 #6b4280, stop: 1 #5a3a70);
                border: 4px solid #f8f9fa;
            }
        """)

        # Position the button in the top-right corner
        self.toggle_button.move(self.main_container.width() - 80, 20)
        self.toggle_button.raise_()  # Bring to front
        self.toggle_button.show()

        # Track toolbar visibility
        self.toolbar_visible = False

        # # Add Point button at the bottom
        # add_point_layout = QHBoxLayout()
        #
        # add_point_btn = TouchButton("+ Add Point", size=(140, 50))  # Made touch-friendly
        # add_point_btn.clicked.connect(self.add_point)
        # add_point_btn.setStyleSheet("""
        #     TouchButton {
        #         background-color: #905BA9;
        #         color: white;
        #         font-weight: bold;
        #         font-size: 14px;
        #         border: 2px solid #905BA9;
        #         border-radius: 8px;
        #         min-width: 140px;
        #         min-height: 50px;
        #     }
        #     TouchButton:hover {
        #         background-color: #7a4d91;
        #         border-color: #7a4d91;
        #     }
        #     TouchButton:pressed {
        #         background-color: #6b4280;
        #         border: 3px solid #6b4280;
        #     }
        # """)
        # add_point_layout.addWidget(add_point_btn)
        # add_point_layout.addStretch()
        #
        # layout.addLayout(add_point_layout)

        self.setStyleSheet("""
            SegmentManager {
                background-color: #f9fafb;
                border-radius: 12px;
            }
        """)

    # python
    def on_layer_visibility_toggled(self, layer_name, visible,onSuccess=None,onFailure=None):
        print(f"Layer '{layer_name}' visibility changed: {visible}")
        self.layerVisibilityToggled.emit(layer_name, visible, onSuccess, onFailure)

    def on_layer_lock_requested(self, layer_name, locked,onSuccess=None,onFailure=None):
        """Handle layer lock toggle"""
        print(f"Layer '{layer_name}' lock status changed: {'locked' if locked else 'unlocked'}")
        # Emit signal to notify other components
        self.layerLockRequested.emit(layer_name, locked, onSuccess, onFailure)
    def on_segment_visibility_toggled(self, segment_name, visible):
        print(f"Segment '{segment_name}' visibility changed: {visible}")
        self.segmentVisibilityToggled.emit(segment_name, visible)
    def on_toggle_toolbar(self):
        # emit signal to toggle toolbar visibility
        self.toggleToolbarRequested.emit()

    def resizeEvent(self, event):
        """Handle resize events to reposition the floating button"""
        super().resizeEvent(event)
        if hasattr(self, 'toggle_button') and hasattr(self, 'main_container'):
            # Reposition the floating button to stay in the top-right corner
            self.toggle_button.move(self.main_container.width() - 80, 20)

    def toggle_toolbar_visibility(self):
        """Toggle the visibility of the toolbar"""
        self.toolbar_visible = not self.toolbar_visible
        self.toolbar.setVisible(self.toolbar_visible)

        # Update button icon to indicate state
        if self.toolbar_visible:
            self.toggle_button.setText("✕")  # Close/hide icon
            self.toggle_button.setToolTip("Hide Toolbar")
        else:
            self.toggle_button.setText("🔧")  # Tools icon
            self.toggle_button.setToolTip("Show Toolbar")

        print(f"🔧 Toolbar {'shown' if self.toolbar_visible else 'hidden'}")

    def populate_demo_data(self):
        """Add demo data with collapsible layers"""
        layers = ["External", "Contour", "Fill"]

        for layer in layers:
            # Initialize layer state
            self.layer_expanded_state[layer] = True
            self.layer_segments[layer] = []
            # self.layer_segment_counters[layer] = 0

            # Add layer header
            header = LayerHeaderItem(layer)
            header.toggleRequested.connect(self.on_layer_toggle)
            header.selectedChanged.connect(lambda layer_name,selected:self.on_layer_selected_changed(layer_name, selected))
            header.layerVisibilityToggled.connect(lambda layer_name,is_visible,onSuccess,onFailure: self.on_layer_visibility_toggled(layer_name, is_visible,onSuccess,onFailure))  # Connect layer visibility toggle
            header.layerLockRequested.connect(lambda layer_name,locked,onSuccess,onFailure :self.on_layer_lock_requested(layer_name, locked, onSuccess, onFailure))  # Connect layer lock toggle
            header.addSegmentRequested.connect(lambda layer_name: self.add_segment(layer_name))  # Connect add segment request

            self.layer_headers[layer] = header
            self.segment_list.add_layer_header(header)

            # # Add segments
            # for i in range(3):
            #     self.add_segment_to_layer(layer, demo_mode=True)

    def add_segment_to_layer(self, layer_name, demo_mode=False):
        """Add a segment to a specific layer with layer-specific numbering"""
        # Get the next segment index for this layer
        layer_seg_index = self.layer_segment_counters+1

        # Create segment with layer-specific ID
        segment = SimpleSegmentItem(layer_seg_index, layer_name)
        segment.selectionChanged.connect(self.on_selection_changed)
        segment.segmentDeleted.connect(self.on_segment_deleted)
        segment.toggleSegmentRequested.connect(self.on_segment_toggle)  # Connect segment toggle
        segment.segmentVisibilityToggled.connect(self.on_segment_visibility_toggled)  # Connect segment visibility toggle
        # Add to layer tracking
        self.layer_segments[layer_name].append(segment)
        self.layer_segment_counters += 1

        # Add to main segments list
        self.segments.append(segment)

        if demo_mode:
            # Use the existing method for demo data
            self.segment_list.add_segment_item(segment, layer_seg_index)
        else:
            # For manual additions, insert at correct position
            insertion_index = self.find_layer_insertion_point(layer_name)

            from PyQt6.QtWidgets import QListWidgetItem
            from PyQt6.QtCore import Qt

            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, {
                'type': 'segment',
                'seg_index': layer_seg_index,
                'layer_name': layer_name,
                'unique_id': f"{layer_name}_{layer_seg_index}"  # Unique identifier
            })
            item.setSizeHint(segment.sizeHint())

            # Insert at the calculated position
            self.segment_list.insertItem(insertion_index, item)
            self.segment_list.setItemWidget(item, segment)

            # Hide if layer is collapsed
            if not self.layer_expanded_state.get(layer_name, True):
                item.setHidden(True)

        return segment

    def find_segment_layer_by_position(self, position):
        """Find which layer a segment at given position should belong to"""
        current_layer = None

        for i in range(min(position + 1, self.segment_list.count())):
            item = self.segment_list.item(i)
            if not item:
                continue

            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue

            if data.get('type') == 'layer':
                current_layer = data.get('layer_name')
            elif data.get('type') == 'segment' and i == position:
                # We found our segment, return the current layer
                return current_layer

        return current_layer

    def transfer_segment_to_layer(self, segment, new_layer_name):
        """Transfer a segment from one layer to another"""
        old_layer_name = segment.layer_name
        old_unique_id = f"{old_layer_name}_{segment.seg_index}"

        print(f"🔄 Transferring segment from '{old_layer_name}' to '{new_layer_name}'")

        # Remove from old layer tracking
        if old_layer_name in self.layer_segments:
            if segment in self.layer_segments[old_layer_name]:
                self.layer_segments[old_layer_name].remove(segment)

        # Add to new layer tracking
        if new_layer_name not in self.layer_segments:
            self.layer_segments[new_layer_name] = []

        # Get new segment index for the target layer
        new_seg_index = len(self.layer_segments[new_layer_name])

        # Update segment properties
        segment.layer_name = new_layer_name
        segment.seg_index = new_seg_index
        segment.update_info_label()

        # Add to new layer
        self.layer_segments[new_layer_name].append(segment)

        # Update selection tracking
        new_unique_id = f"{new_layer_name}_{new_seg_index}"
        if old_unique_id in self.selected_segments:
            self.selected_segments.discard(old_unique_id)
            self.selected_segments.add(new_unique_id)

        # Update the list item data
        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if item:
                widget = self.segment_list.itemWidget(item)
                if widget is segment:
                    item.setData(Qt.ItemDataRole.UserRole, {
                        'type': 'segment',
                        'seg_index': new_seg_index,
                        'layer_name': new_layer_name,
                        'unique_id': new_unique_id
                    })
                    break

        print(
            f"✅ Segment transferred: {old_layer_name}-S{segment.seg_index:02d} → {new_layer_name}-S{new_seg_index:02d}")

    # python
    def on_layer_selected_changed(self, layer_name, selected):
        for name, header in self.layer_headers.items():
            header.mark_layer_unselected()
            print(f"📁 Layer '{name}' unselected")

        if selected and layer_name in self.layer_headers:
            self.layer_headers[layer_name].mark_layer_selected()
            self.selected_layer = layer_name
            print(f"📁 Layer '{layer_name}' selected")
            print("Selected layer set to:", self.selected_layer)
        else:
            self.selected_layer = None
            print("📁 No layer selected")
            print("Selected layer: ",selected)
            print("Layer name: ",layer_name)
            print(self.layer_headers)

        print(f"📁 Layer '{layer_name}' {'selected' if selected else 'deselected'}")
    def on_layer_toggle(self, layer_name, is_expanded):
        """Handle layer collapse/expand"""
        print(f"📁 Layer '{layer_name}' {'expanded' if is_expanded else 'collapsed'}")

        self.layer_expanded_state[layer_name] = is_expanded

        if is_expanded:
            self.segment_list.show_layer_segments(layer_name)
        else:
            self.segment_list.hide_layer_segments(layer_name)

    def on_segment_toggle(self, layer_name, is_expanded):
        """Handle segment collapse/expand - hide/show points within a segment"""
        # Find the segment that sent this signal
        sending_segment = self.sender()
        if not isinstance(sending_segment, SimpleSegmentItem):
            return

        seg_index = sending_segment.seg_index
        print(f"📋 Segment '{layer_name}-S{seg_index:02d}' {'expanded' if is_expanded else 'collapsed'}")

        # Find all points belonging to this segment and hide/show them
        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if not item:
                continue

            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue

            # Check if this is a point belonging to our segment
            if (data.get('type') == 'point' and
                    data.get('layer_name') == layer_name and
                    data.get('seg_index') == seg_index):

                # Show/hide the point based on segment expansion state
                if is_expanded:
                    # Only show if the parent layer is also expanded
                    layer_expanded = self.layer_expanded_state.get(layer_name, True)
                    item.setHidden(not layer_expanded)
                else:
                    # Hide the point
                    item.setHidden(True)

        print(f"✅ Points in segment {layer_name}-S{seg_index:02d} {'shown' if is_expanded else 'hidden'}")

    def expand_all_layers(self):
        """Expand all layers"""
        for layer_name, header in self.layer_headers.items():
            if not header.is_expanded:
                header.set_expanded(True)
                self.layer_expanded_state[layer_name] = True
                self.segment_list.show_layer_segments(layer_name)
        print("📁 All layers expanded")

    def collapse_all_layers(self):
        """Collapse all layers"""
        for layer_name, header in self.layer_headers.items():
            if header.is_expanded:
                header.set_expanded(False)
                self.layer_expanded_state[layer_name] = False
                self.segment_list.hide_layer_segments(layer_name)
        print("📁 All layers collapsed")

    def on_segment_moved(self, seg_index, new_position):
        """Handle segment movement with layer transfer detection"""
        print(f"📋 Segment moved to position {new_position}")

        # Find the segment that was moved
        moved_segment = None
        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if item and i == new_position:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data and data.get('type') == 'segment':
                    moved_segment = self.segment_list.itemWidget(item)
                    break

        if moved_segment and isinstance(moved_segment, SimpleSegmentItem):
            # Determine which layer this position should belong to
            target_layer = self.find_segment_layer_by_position(new_position)

            if target_layer and target_layer != moved_segment.layer_name:
                # Transfer segment to new layer
                self.transfer_segment_to_layer(moved_segment, target_layer)

        # Renumber all segments in all layers
        self.renumber_all_layer_segments()

    def renumber_all_layer_segments(self):
        """Renumber segments within each layer separately after any movement"""
        print("🔄 Renumbering all segments per layer...")

        # Reset layer counters and segment lists
        for layer_name in self.layer_segments:
            self.layer_segments[layer_name] = []

        # Collect segments by layer in their current order
        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if item and not item.isHidden():
                data = item.data(Qt.ItemDataRole.UserRole)
                if data and data.get('type') == 'segment':
                    widget = self.segment_list.itemWidget(item)
                    if isinstance(widget, SimpleSegmentItem):
                        layer_name = widget.layer_name

                        # Get new index for this layer
                        new_layer_index = len(self.layer_segments[layer_name])
                        old_index = widget.seg_index
                        old_unique_id = f"{layer_name}_{old_index}"

                        # Update the segment
                        widget.seg_index = new_layer_index
                        widget.update_info_label()

                        # Update item data
                        new_unique_id = f"{layer_name}_{new_layer_index}"
                        data['seg_index'] = new_layer_index
                        data['unique_id'] = new_unique_id
                        item.setData(Qt.ItemDataRole.UserRole, data)

                        # Add to layer tracking
                        self.layer_segments[layer_name].append(widget)

                        # Update selection tracking with unique ID
                        if old_unique_id in self.selected_segments:
                            self.selected_segments.discard(old_unique_id)
                            self.selected_segments.add(new_unique_id)

                        if old_index != new_layer_index:
                            print(f"  📝 {layer_name}: S{old_index:02d} → S{new_layer_index:02d}")

        # Update layer counters
        # for layer_name in self.layer_segments:
        #     self.layer_segment_counters[layer_name] = len(self.layer_segments[layer_name])

        # Force list widget update
        self.segment_list.update()
        self.segment_list.repaint()

        self.update_status()
        print("✅ Layer-based renumbering complete")

    def renumber_layer_segments(self):
        """Legacy method - now calls the new comprehensive renumbering"""
        self.renumber_all_layer_segments()

    # python
    def on_selection_changed(self, seg_index, selected):
        print(f"🔄 Selection changed for segment S{seg_index:02d}: {'selected' if selected else 'deselected'}")
        """Handle selection changes using unique segment ID"""
        segment_widget = self.sender()
        # clear all selected first
        if len(self.selected_segments) > 0:
            print("⚠️ Multiple segments selected, clearing previous selections")
            self.clear_selection()
            # Mark the current segment as selected if needed
            if selected and isinstance(segment_widget, SimpleSegmentItem):
                segment_widget.set_selected(True)
                print(f"➕ Segment {segment_widget.layer_name}-S{seg_index:02d} selected")
        if isinstance(segment_widget, SimpleSegmentItem):
            unique_id = f"{segment_widget.layer_name}_{seg_index}"

            if selected:
                self.selected_segments.add(unique_id)
            else:
                self.selected_segments.discard(unique_id)

            self.update_status()

        self.selectedSegmentChanged.emit(seg_index, selected)

    # python
    def on_segment_deleted(self, seg_index):
        """Handle segment deletion"""
        segment_to_delete = None
        layer_name = None

        # First, find the segment to delete
        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if item:
                data = item.data(Qt.ItemDataRole.UserRole)
                if data and data.get('type') == 'segment':
                    widget = self.segment_list.itemWidget(item)
                    if isinstance(widget, SimpleSegmentItem) and widget.seg_index == seg_index:
                        segment_to_delete = widget
                        layer_name = widget.layer_name
                        break

        # Delete all points belonging to this segment
        if segment_to_delete and layer_name:
            points_to_delete = []
            for i in range(self.segment_list.count()):
                item = self.segment_list.item(i)
                if item:
                    data = item.data(Qt.ItemDataRole.UserRole)
                    if (data and data.get('type') == 'point' and
                            data.get('layer_name') == layer_name and
                            data.get('seg_index') == seg_index):
                        points_to_delete.append(i)
            # Remove points in reverse order to avoid index shifting
            for i in reversed(points_to_delete):
                self.segment_list.takeItem(i)

            # Now remove the segment itself
            for i in range(self.segment_list.count()):
                item = self.segment_list.item(i)
                if item:
                    data = item.data(Qt.ItemDataRole.UserRole)
                    if data and data.get('type') == 'segment':
                        widget = self.segment_list.itemWidget(item)
                        if widget is segment_to_delete:
                            if widget in self.segments:
                                self.segments.remove(widget)
                            if layer_name in self.layer_segments and widget in self.layer_segments[layer_name]:
                                self.layer_segments[layer_name].remove(widget)
                            self.segment_list.takeItem(i)
                            break

            unique_id = f"{layer_name}_{seg_index}"
            self.selected_segments.discard(unique_id)
            print(f"🗑️ Deleted segment {layer_name}-S{seg_index:02d}")

            # Renumber remaining segments in this layer
            self.renumber_all_layer_segments()

    def select_all(self):
        """Select all visible segments"""
        self.selected_segments.clear()
        for layer_name, segments in self.layer_segments.items():
            if self.layer_expanded_state.get(layer_name, True):
                for segment in segments:
                    segment.set_selected(True)
                    unique_id = f"{layer_name}_{segment.seg_index}"
                    self.selected_segments.add(unique_id)
        self.update_status()

    def clear_selection(self):
        """Clear all selections"""
        for layer_name, segments in self.layer_segments.items():
            for segment in segments:
                segment.set_selected(False)
        self.selected_segments.clear()
        self.update_status()

    def add_segment(self,layer_name):
        print("In add_segment method")
        """Add a new segment to the currently selected layer"""
        # if not self.layer_headers or not self.selected_layer:
        #     print("⚠️ No layer selected or no layers available")
        #     toast = ToastWidget(self, message="No layer selected or available", duration=3000)
        #     toast.show()
        #     return
        # else:
        #     print(f"🔧 Adding segment to layer: {self.selected_layer}")

        target_layer = layer_name
        print(f"🎯 Adding segment to layer: {target_layer}")

        def onSucccess(newSegment):
            print(f"➕ Segment added successfully to layer {target_layer}")
            try:
                segment = self.add_segment_to_layer(target_layer)

                layer_seg_index = segment.seg_index
                # layer_seg_index = newSegment.index

                print(f"➕ Successfully added segment {target_layer}-S{layer_seg_index:02d}")
                self.update_status()

            except Exception as e:
                print(f"❌ Error adding segment: {e}")

        def onFailure():
            print(f"❌ Failed to add segment to layer {target_layer}")
            toast = ToastWidget(self ,message=f"Failed to add segment to layer {target_layer}",duration=3000)
            toast.show()

        self.addSegmentRequested.emit(target_layer,onSucccess,onFailure)


        # result = self.addSegmentRequested.emit()
        # print(f"🔧 addSegmentRequested signal emitted: {result}")
        # if not result:
        #     print("❌ Failed to add segment: addSegmentRequested signal did not return True")
        #     return



    def add_point(self, point):
        """Add a new PointItem under the currently selected segment"""
        if len(self.selected_segments) > 1:
            print("⚠️ Multiple segments selected, please select a single segment to add a point")
            return
        if len(self.selected_segments) == 0:
            print("⚠️ No segment selected, please select a segment to add a point")
            return

        unique_id = next(iter(self.selected_segments))  # Get the only selected segment's unique_id

        try:
            point = self.add_point_to_segment(unique_id, point)
            print(f"➕ Point added to segment {unique_id}")
        except Exception as e:
            print(f"❌ Error adding point: {e}")

    def add_point_to_segment(self, segment_unique_id, point):
        """Add a point to a specific segment using its unique ID"""
        # Parse the unique ID to get layer name and segment index
        layer_name, seg_index = segment_unique_id.rsplit("_", 1)
        seg_index = int(seg_index)

        print(f"🎯 Adding point to segment {layer_name}-S{seg_index:02d}")

        # Find the target segment widget
        target_segment = None
        for segment in self.layer_segments.get(layer_name, []):
            if segment.seg_index == seg_index:
                target_segment = segment
                break

        if not target_segment:
            raise Exception(f"Could not find segment {layer_name}-S{seg_index:02d}")

        # Find the segment's insertion point in the list widget
        insertion_index = self.find_segment_insertion_point(layer_name, seg_index)

        # Get the next point index for this segment
        point_index = getattr(target_segment, 'point_count', 0)

        # Create the PointItem
        point_item = PointItem(point_index, point.x(), point.y())

        # Connect the point deletion signal
        point_item.pointDeleted.connect(lambda idx: self.on_point_deleted(idx, layer_name, seg_index))

        # Create list widget item
        from PyQt6.QtWidgets import QListWidgetItem

        point_list_item = QListWidgetItem()
        point_list_item.setData(Qt.ItemDataRole.UserRole, {
            'type': 'point',
            'point_index': point_index,
            'seg_index': seg_index,
            'layer_name': layer_name,
            'unique_id': f"{layer_name}_{seg_index}_P{point_index:02d}"
        })
        point_list_item.setSizeHint(point_item.sizeHint())

        # Insert point at the calculated position
        self.segment_list.insertItem(insertion_index, point_list_item)
        self.segment_list.setItemWidget(point_list_item, point_item)

        # Update point count on segment
        if not hasattr(target_segment, 'point_count'):
            target_segment.point_count = 0
        target_segment.point_count += 1

        # Hide if layer is collapsed OR if segment is collapsed
        layer_expanded = self.layer_expanded_state.get(layer_name, True)
        segment_expanded = target_segment.is_expanded
        point_list_item.setHidden(not (layer_expanded and segment_expanded))

        return point_item

    def find_segment_insertion_point(self, target_layer, target_seg_index):
        """Find where to insert a new point for the given segment"""
        segment_found = False
        last_point_in_segment = None

        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if not item:
                continue

            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue

            # Found the target segment
            if (data.get('type') == 'segment' and
                    data.get('layer_name') == target_layer and
                    data.get('seg_index') == target_seg_index):
                segment_found = True
                last_point_in_segment = i + 1  # Position after segment
                continue

            # If we're past the target segment, check for points
            if segment_found:
                if data.get('type') == 'point':
                    if (data.get('layer_name') == target_layer and
                            data.get('seg_index') == target_seg_index):
                        # This point belongs to our target segment
                        last_point_in_segment = i + 1  # Position after this point
                    else:
                        # We've hit a point from a different segment, stop here
                        break
                elif data.get('type') in ['segment', 'layer']:
                    # We've hit another segment or layer, stop here
                    break

        # Return the position where we should insert
        return last_point_in_segment if last_point_in_segment is not None else self.segment_list.count()

    def find_layer_insertion_point(self, target_layer):
        """Find where to insert a new segment for the given layer"""
        layer_header_found = False
        last_segment_in_layer = None

        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if not item:
                continue

            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue

            # Found the target layer header
            if data.get('type') == 'layer' and data.get('layer_name') == target_layer:
                layer_header_found = True
                last_segment_in_layer = i + 1  # Position after header
                continue

            # If we're past the target layer header, check for segments
            if layer_header_found:
                if data.get('type') == 'segment':
                    widget = self.segment_list.itemWidget(item)
                    if isinstance(widget, SimpleSegmentItem) and widget.layer_name == target_layer:
                        # This segment belongs to our target layer
                        last_segment_in_layer = i + 1  # Position after this segment
                    else:
                        # We've hit a segment from a different layer, stop here
                        break
                elif data.get('type') == 'layer':
                    # We've hit another layer header, stop here
                    break

        # Return the position where we should insert
        return last_segment_in_layer if last_segment_in_layer is not None else self.segment_list.count()

    def update_status(self):
        """Update status label"""
        count = len(self.selected_segments)
        total_visible = 0

        for layer_name, segments in self.layer_segments.items():
            if self.layer_expanded_state.get(layer_name, True):
                total_visible += len(segments)

        # Update toolbar status
        self.toolbar.update_status(count, total_visible)

    def on_point_deleted(self, point_index, layer_name, seg_index):
        """Handle point deletion"""
        print(f"🗑️ Deleting point P{point_index:02d} from segment {layer_name}-S{seg_index:02d}")

        # Find and remove the point from the list
        point_to_delete = None
        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if not item:
                continue

            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue

            # Check if this is the point we want to delete
            if (data.get('type') == 'point' and
                    data.get('layer_name') == layer_name and
                    data.get('seg_index') == seg_index and
                    data.get('point_index') == point_index):
                # Remove from list
                self.segment_list.takeItem(i)
                point_to_delete = True
                break

        if point_to_delete:
            # Update point count on the parent segment
            target_segment = None
            for segment in self.layer_segments.get(layer_name, []):
                if segment.seg_index == seg_index:
                    target_segment = segment
                    break

            if target_segment and hasattr(target_segment, 'point_count'):
                target_segment.point_count = max(0, target_segment.point_count - 1)

            # Renumber remaining points in this segment
            self.renumber_points_in_segment(layer_name, seg_index)

            print(f"✅ Point P{point_index:02d} deleted from {layer_name}-S{seg_index:02d}")
        else:
            print(f"❌ Could not find point P{point_index:02d} in {layer_name}-S{seg_index:02d}")

    def renumber_points_in_segment(self, layer_name, seg_index):
        """Renumber points within a specific segment after deletion"""
        print(f"🔄 Renumbering points in segment {layer_name}-S{seg_index:02d}")

        points_in_segment = []

        # Collect all points belonging to this segment
        for i in range(self.segment_list.count()):
            item = self.segment_list.item(i)
            if not item:
                continue

            data = item.data(Qt.ItemDataRole.UserRole)
            if not data:
                continue

            if (data.get('type') == 'point' and
                    data.get('layer_name') == layer_name and
                    data.get('seg_index') == seg_index):

                widget = self.segment_list.itemWidget(item)
                if isinstance(widget, PointItem):
                    points_in_segment.append((i, item, widget))

        # Sort by current list position to maintain order
        points_in_segment.sort(key=lambda x: x[0])

        # Renumber points sequentially
        for new_index, (list_index, item, widget) in enumerate(points_in_segment):
            old_index = widget.index

            # Update the point widget
            widget.index = new_index
            widget.update_index(new_index)

            # Update item data
            data = item.data(Qt.ItemDataRole.UserRole)
            data['point_index'] = new_index
            data['unique_id'] = f"{layer_name}_{seg_index}_P{new_index:02d}"
            item.setData(Qt.ItemDataRole.UserRole, data)

            if old_index != new_index:
                print(f"  📝 {layer_name}-S{seg_index:02d}: P{old_index:02d} → P{new_index:02d}")

        print(f"✅ Point renumbering complete for segment {layer_name}-S{seg_index:02d}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = SegmentManager()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
