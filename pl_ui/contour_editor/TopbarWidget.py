import os
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy,
    QMessageBox, QApplication, QSpacerItem
)
from pl_ui.utils.IconLoader import PICKUP_POINT_ICON

ICON_WIDTH = 64
ICON_HEIGHT = 64

RESOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

REMOVE_ICON = os.path.join(RESOURCE_DIR, "remove.png")
UNDO_ICON = os.path.join(RESOURCE_DIR, "undo.png")
REDO_ICON = os.path.join(RESOURCE_DIR, "redo.png")
DRAG_ICON = os.path.join(RESOURCE_DIR, "drag.png")
PREVIEW_ICON = os.path.join(RESOURCE_DIR, "preview.png")
RESET_ZOOM_ICON = os.path.join(RESOURCE_DIR, "reset_zoom.png")
ZIGZAG_ICON = os.path.join(RESOURCE_DIR, "zigzag.png")
OFFSET_ICON = os.path.join(RESOURCE_DIR, "offset.png")
POINTER_ICON = os.path.join(RESOURCE_DIR, "pointer.png")
SAVE_ICON = os.path.join(RESOURCE_DIR, "SAVE_BUTTON.png")
ZOOM_IN = os.path.join(RESOURCE_DIR, "zoom_in.png")
ZOOM_OUT = os.path.join(RESOURCE_DIR, "zoom_out.png")


class TopBarWidget(QWidget):
    def __init__(self, contour_editor=None, point_manager=None, save_button_callback=None,onStartCallback = None,zigzag_callback=None, offset_callback=None):
        super().__init__()

        self.zigzag_callback = zigzag_callback
        self.offset_callback = offset_callback
        self.contour_editor = contour_editor
        self.point_manager = point_manager
        self.save_button_callback = save_button_callback
        self.onStartCallback = onStartCallback
        self.setMinimumHeight(50)
        self.setMaximumHeight(150)
        self.setMinimumWidth(300)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left section (Undo/Redo)
        self.left_layout = QHBoxLayout()
        self.left_layout.setSpacing(0)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.undo_button = self.create_button(UNDO_ICON, self.undo_action)
        self.redo_button = self.create_button(REDO_ICON, self.redo_action)
        self.left_layout.addWidget(self.undo_button)
        self.left_layout.addWidget(self.redo_button)

        # Center section (other buttons)
        self.center_layout = QHBoxLayout()
        self.center_layout.setSpacing(0)
        self.center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.remove_button = self.create_button(REMOVE_ICON, self.dummy_remove_action)
        self.remove_button.setToolTip("Remove selected point(s)\nLong press to enter multi-selection mode")
        self.mode_toggle_button = self.create_button(DRAG_ICON, self.toggle_cursor_mode)
        self.pickup_point_button = self.create_button(PICKUP_POINT_ICON, self.toggle_pickup_point_mode)
        self.pickup_point_button.setToolTip("Pickup Point Mode - Click to set gripper pickup location")
        self.pickup_point_button.setCheckable(True)


        self.preview_path_button = self.create_button(PREVIEW_ICON, self.on_preview)
        self.zigzag_button = self.create_button(ZIGZAG_ICON, self.on_zigzag)
        self.offset_button = self.create_button(OFFSET_ICON, self.on_offset)

        self.add_spacer(self.center_layout)

        self.zoom_out_button = self.create_button(ZOOM_OUT, self.on_zoom_out)
        self.reset_zoom_button = self.create_button(RESET_ZOOM_ICON, self.reset_zoom)
        self.zoom_in_button = self.create_button(ZOOM_IN, self.on_zoom_in)

        self.center_layout.addWidget(self.remove_button)
        self.center_layout.addWidget(self.mode_toggle_button)
        self.center_layout.addWidget(self.pickup_point_button)
        self.center_layout.addWidget(self.preview_path_button)
        self.center_layout.addWidget(self.zigzag_button)
        self.center_layout.addWidget(self.offset_button)

        self.center_layout.addStretch()

        self.center_layout.addWidget(self.zoom_out_button)
        self.center_layout.addWidget(self.reset_zoom_button)
        self.center_layout.addWidget(self.zoom_in_button)

        # for btn in [
        #     self.remove_button, self.mode_toggle_button, self.preview_path_button,
        #     self.zigzag_button, self.offset_button,
        #     self.zoom_out_button, self.reset_zoom_button, self.zoom_in_button
        # ]:
        #     self.center_layout.addWidget(btn)

        # Right section (Save)
        self.right_layout = QHBoxLayout()
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.startButton = QPushButton("Start")

        self.startButton.setStyleSheet("border: none; padding: 5px; margin: 5px;")


        self.startButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.startButton.clicked.connect(self.onStart)

        self.save_button = self.create_button(SAVE_ICON, save_button_callback or self.on_save)
        self.right_layout.addWidget(self.startButton)
        self.right_layout.addWidget(self.save_button)

        # Add all to main layout
        main_layout.addLayout(self.left_layout)
        main_layout.addStretch()
        main_layout.addLayout(self.center_layout)
        main_layout.addStretch()
        main_layout.addLayout(self.right_layout)

        self.buttons = [self.remove_button, self.mode_toggle_button, self.pickup_point_button, self.preview_path_button,
                        self.zigzag_button, self.offset_button,
                        self.zoom_out_button, self.reset_zoom_button, self.zoom_in_button, self.undo_button,
                        self.redo_button, self.save_button]

        self.setLayout(main_layout)

        self.is_drag_mode = False
        self.multi_select_mode_active = False
        
        # Setup long press functionality for remove button
        self.setup_remove_button_long_press()

    def dummy_remove_action(self):
        """Dummy action for remove button - actual logic handled in mouse events"""
        pass

    def onStart(self):
        print("Start button pressed")

        if self.onStartCallback:

            self.onStartCallback()

    def add_spacer(self, layout=None, width=20):
        if layout is None:
            layout = self.center_layout  # Default to center if none provided
        spacer = QWidget()
        spacer.setFixedWidth(width)
        layout.addWidget(spacer)

    def set_save_button_callback(self, callback):
        self.save_button.clicked.connect(callback)

    def create_button(self, icon_path, click_handler, text=None):
        button = QPushButton("")
        if icon_path:
            button.setIcon(QIcon(icon_path))
        if text:
            button.setText(text)
        button.setStyleSheet("border: none; padding: 5px; margin: 5px;")
        button.setIconSize(QSize(ICON_WIDTH, ICON_HEIGHT))
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.clicked.connect(click_handler)
        return button

    def on_zoom_in(self):
        print("Zooming in")
        self.contour_editor.zoom_in()

    def on_zoom_out(self):
        print("Zooming out")
        self.contour_editor.zoom_out()

    def on_save(self):
        print("Save button pressed")

    def on_zigzag(self):
        print("Zigzag button clicked")
        if self.zigzag_callback is not None:
            self.zigzag_callback()

    def on_offset(self):
        print("Offset button clicked")
        if self.offset_callback is not None:
            self.offset_callback()

    def on_preview(self):
        self.contour_editor.save_robot_path_to_txt("preview.txt", samples_per_segment=5)
        self.contour_editor.plot_robot_path("preview.txt")

    def reset_zoom(self):
        if not self.contour_editor:
            QMessageBox.warning(self, "Error", "Contour editor is not set.")
            return
        try:
            self.contour_editor.reset_zoom()
            self.contour_editor.update()
        except Exception as e:
            QMessageBox.critical(self, "Reset Zoom Failed", str(e))

    def toggle_cursor_mode(self):
        if not self.contour_editor:
            QMessageBox.warning(self, "Error", "Contour editor is not set.")
            return

        self.is_drag_mode = not self.is_drag_mode
        new_mode = "drag" if self.is_drag_mode else "edit"

        try:
            self.contour_editor.set_cursor_mode(new_mode)
            icon = POINTER_ICON if self.is_drag_mode else DRAG_ICON
            self.mode_toggle_button.setIcon(QIcon(icon))
        except Exception as e:
            QMessageBox.critical(self, "Mode Toggle Failed", str(e))

    def toggle_pickup_point_mode(self):
        """Toggle pickup point mode on/off"""
        if not self.contour_editor:
            QMessageBox.warning(self, "Error", "Contour editor is not set.")
            return

        try:
            is_pickup_mode = self.pickup_point_button.isChecked()
            
            if is_pickup_mode:
                # Exit multi-select mode if active
                if hasattr(self.contour_editor, 'multi_select_mode_active') and self.contour_editor.multi_select_mode_active:
                    self.exit_multi_select_mode()
                
                # Switch to pickup point mode
                self.contour_editor.set_cursor_mode("pickup_point")
                self.pickup_point_button.setStyleSheet("border: none; padding: 5px; margin: 5px; background-color: #6750A4;")
                print("Pickup point mode activated")
            else:
                # Switch back to edit mode
                self.contour_editor.set_cursor_mode("edit")
                self.pickup_point_button.setStyleSheet("border: none; padding: 5px; margin: 5px;")
                print("Pickup point mode deactivated")
                
        except Exception as e:
            QMessageBox.critical(self, "Pickup Point Mode Toggle Failed", str(e))

    def setup_remove_button_long_press(self):
        """Setup long press functionality for the remove button"""
        self.long_press_timer = QTimer()
        self.long_press_timer.setSingleShot(True)
        self.long_press_timer.timeout.connect(self.enter_multi_select_mode)
        
        # Override the remove button's mouse events
        self.remove_button.mousePressEvent = self.remove_button_mouse_press
        self.remove_button.mouseReleaseEvent = self.remove_button_mouse_release
        
    def remove_button_mouse_press(self, event):
        """Handle mouse press on remove button - start long press timer"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.long_press_timer.start(800)  # 800ms for long press
            # Call the original press event
            QPushButton.mousePressEvent(self.remove_button, event)
    
    def remove_button_mouse_release(self, event):
        """Handle mouse release on remove button"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.long_press_timer.isActive():
                # Short press - normal remove action
                self.long_press_timer.stop()
                self.remove_selected_point()
            # Call the original release event 
            QPushButton.mouseReleaseEvent(self.remove_button, event)
    
    def enter_multi_select_mode(self):
        """Toggle multi-selection mode via long press"""
        if not self.contour_editor:
            return
        
        if self.multi_select_mode_active:
            # Already in multi-select mode, exit it
            self.exit_multi_select_mode()
        else:
            # Enter multi-select mode
            self.multi_select_mode_active = True
            
            # Exit pickup point mode if active
            if self.pickup_point_button.isChecked():
                self.pickup_point_button.setChecked(False)
                self.pickup_point_button.setStyleSheet("border: none; padding: 5px; margin: 5px;")
            
            # Switch to multi-select mode
            self.contour_editor.set_cursor_mode("multi_select")
            self.remove_button.setStyleSheet("border: none; padding: 5px; margin: 5px; background-color: #6750A4;")
            self.remove_button.setToolTip("Multi-Selection Mode Active\nClick points to select/deselect\nShort press to delete selected points\nLong press again to exit")
            print("Multi-selection mode activated via long press")
    
    def exit_multi_select_mode(self):
        """Exit multi-selection mode"""
        if not self.contour_editor:
            return
            
        self.multi_select_mode_active = False
        
        # Clear all selections
        if hasattr(self.contour_editor, 'clear_all_selections'):
            self.contour_editor.clear_all_selections()
        
        # Switch back to edit mode
        self.contour_editor.set_cursor_mode("edit")
        self.remove_button.setStyleSheet("border: none; padding: 5px; margin: 5px;")
        self.remove_button.setToolTip("Remove selected point(s)\nLong press to enter multi-selection mode")
        print("Multi-selection mode deactivated")

    def undo_action(self):
        if not self.contour_editor:
            print("Error", "Contour editor is not set.")
            # QMessageBox.warning(self, "Error", "Contour editor is not set.")
            return
        try:
            self.contour_editor.manager.undo()
            self.point_manager.refresh_points()
            self.contour_editor.update()
        except Exception as e:
            QMessageBox.critical(self, "Undo Failed", str(e))

    def redo_action(self):
        if not self.contour_editor:
            print("Error", "Contour editor is not set.")
            # QMessageBox.warning(self, "Error", "Contour editor is not set.")
            return
        try:
            self.contour_editor.manager.redo()
            self.point_manager.refresh_points()
            self.contour_editor.update()
        except Exception as e:
            QMessageBox.critical(self, "Redo Failed", str(e))

    def remove_selected_point(self):
        """Remove the currently selected point(s) - supports both single and multi-selection"""
        if not self.contour_editor or not self.point_manager:
            QMessageBox.warning(self, "Error", "Contour editor or point manager is not set.")
            return
            
        # Check if any points are selected (multi-selection takes priority)
        selected_points_list = getattr(self.contour_editor, 'selected_points_list', [])
        selected_point_info = getattr(self.contour_editor, 'selected_point_info', None)
        
        if selected_points_list:
            # Multi-selection deletion
            self._remove_multiple_points(selected_points_list)
        elif selected_point_info:
            # Single selection deletion (backward compatibility)
            self._remove_single_point(selected_point_info)
        else:
            QMessageBox.information(self, "No Selection", "Please select one or more points first by clicking on them in the display or point manager.\n\nTip: Hold Ctrl and click multiple points for multi-selection.")
            return
    
    def _remove_multiple_points(self, selected_points_list):
        """Remove multiple selected points"""
        try:
            points_count = len(selected_points_list)
            
            # Ask for confirmation when deleting multiple points
            if points_count > 1:
                reply = QMessageBox.question(
                    self, 
                    "Delete Multiple Points", 
                    f"Are you sure you want to delete {points_count} selected points?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Sort points for safe deletion (reverse order by segment and point index)
            sorted_points = sorted(
                selected_points_list,
                key=lambda x: (x['seg_index'], x['point_index']),
                reverse=True
            )
            
            print(f"Deleting {points_count} points: {sorted_points}")
            
            # Save state once for the entire multi-delete operation
            self.contour_editor.manager.save_state()
            
            # Remove all selected points
            for point_info in sorted_points:
                role = point_info['role']
                seg_index = point_info['seg_index']
                point_index = point_info['point_index']
                
                # Validate the point data
                if role not in ['anchor', 'control']:
                    print(f"Warning: Skipping unknown point type: {role}")
                    continue
                
                # Remove the point (without saving state for each deletion)
                segments = self.contour_editor.manager.get_segments()
                if 0 <= seg_index < len(segments):
                    segment = segments[seg_index]
                    if role == 'anchor' and 0 <= point_index < len(segment.points):
                        segment.remove_point(point_index)
                    elif role == 'control' and 0 <= point_index < len(segment.controls):
                        segment.controls[point_index] = None
            
            # Clear all selections
            self.contour_editor.clear_all_selections()
            
            # Refresh the UI
            self.point_manager.refresh_points()
            self.contour_editor.update()
            
            print(f"Successfully deleted {points_count} points")
            
        except Exception as e:
            QMessageBox.critical(self, "Delete Points Failed", f"Error deleting multiple points: {str(e)}")
            print(f"Error in _remove_multiple_points: {e}")
    
    def _remove_single_point(self, selected_point_info):
        """Remove a single selected point (backward compatibility)"""
        try:
            # Extract point information from selected_point_info tuple: (role, seg_index, point_index)
            role, seg_index, point_index = selected_point_info
            
            # Validate the point data
            if role not in ['anchor', 'control']:
                QMessageBox.warning(self, "Invalid Selection", f"Unknown point type: {role}")
                return
                
            # Remove the point using the manager (this automatically saves state for undo)
            self.contour_editor.manager.remove_point(role, seg_index, point_index)
            
            # Clear the selection since the point no longer exists
            self.contour_editor.clear_all_selections()
            
            # Refresh the UI
            self.point_manager.refresh_points()
            self.contour_editor.update()
            
            print(f"Deleted {role} point {point_index} from segment {seg_index}")
            
        except Exception as e:
            QMessageBox.critical(self, "Delete Point Failed", f"Error deleting point: {str(e)}")
            print(f"Error in remove_selected_point: {e}")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    widget = TopBarWidget()
    widget.show()
    sys.exit(app.exec())
