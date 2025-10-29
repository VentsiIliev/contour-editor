import os
import sys

import numpy as np
from shapely import Polygon

from pl_ui.contour_editor.SpacingDialog import SpacingDialog

from pl_ui.contour_editor.utils import shrink_contour_points

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

import cv2
from PyQt6.QtCore import QTimer
from matplotlib import pyplot as plt

from PyQt6.QtCore import Qt, QPointF, pyqtSignal, QEvent, QSize, QRectF
from PyQt6.QtGui import QPainter, QImage, QPen, QBrush, QPainterPath
from PyQt6.QtWidgets import QFrame, QDialog
from PyQt6.QtGui import QColor

from API.shared.contour_editor.BezierSegmentManager import BezierSegmentManager
from pl_ui.contour_editor.SegmentSettingsWidget import default_settings
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.geometry import Polygon

from shapely.geometry import Polygon
from PyQt6.QtCore import QPointF
import numpy as np
import numpy as np
LAYER_COLORS = {
    "Workpiece": QColor("#FF0000"),  # Red
    "Contour": QColor("#00FFFF"),  # Cyan
    "Fill": QColor("#00FF00"),  # Green
}

DRAG_MODE = "drag"
EDIT_MODE = "edit"
PICKUP_POINT_MODE = "pickup_point"
MULTI_SELECT_MODE = "multi_select"


class ContourEditor(QFrame):
    pointsUpdated = pyqtSignal()

    def __init__(self, visionSystem, image_path=None, contours=None, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Editable Bezier Curves")
        self.setGeometry(100, 100, 640, 360)
        self.visionSystem = visionSystem
        self.manager = BezierSegmentManager()
        self.dragging_point = None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setAutoFillBackground(False)
        self.image = self.load_image(image_path)
        self.selected_point_info = None

        self.scale_factor = 1.0
        self.translation = QPointF(0, 0)
        self.grabGesture(Qt.GestureType.PinchGesture)

        self.is_zooming = False

        self.drag_mode_active = False
        self.last_drag_pos = None
        self.contours = None

        self.drag_threshold = 10  # Set a threshold for movement

        self.dragging_point = None
        self.last_drag_pos = None
        self.drag_threshold = 10
        self.drag_timer = QTimer(self)
        self.drag_timer.setInterval(16)  # Limit updates to ~60 FPS
        self.drag_timer.timeout.connect(self.perform_drag_update)
        self.pending_drag_update = False

        # Pickup point functionality
        self.pickup_point_mode_active = False
        self.pickup_point = None

        # Multi-point selection functionality
        self.multi_select_mode_active = False
        self.selected_points_list = []  # List of selected points for multi-selection

        self.initContour(contours)

    def zoom_in(self):
        self._apply_centered_zoom(1.25)

    def zoom_out(self):
        self._apply_centered_zoom(0.8)

    def _apply_centered_zoom(self, factor):
        # Center of the widget in screen space
        center_screen = QPointF(self.width() / 2, self.height() / 2)

        # Convert screen center to image space
        center_img_space = (center_screen - self.translation) / self.scale_factor

        # Apply the zoom factor
        self.scale_factor *= factor

        # Calculate new screen position of image center after scaling
        new_center_screen_pos = center_img_space * self.scale_factor + self.translation

        # Adjust translation so that the zoom is centered on the widget center
        self.translation += center_screen - new_center_screen_pos

        self.update()

    def reset_zoom(self):
        self.scale_factor = 1.0

        # Center image in widget
        frame_width = self.width()
        frame_height = self.height()
        img_width = self.image.width()
        img_height = self.image.height()

        x = (frame_width - img_width) / 2
        y = (frame_height - img_height) / 2
        self.translation = QPointF(x, y)

        self.update()

    def set_cursor_mode(self, mode):
        self.current_mode = mode
        self.drag_mode_active = (mode == DRAG_MODE)
        self.pickup_point_mode_active = (mode == PICKUP_POINT_MODE)
        self.multi_select_mode_active = (mode == MULTI_SELECT_MODE)

        if mode == DRAG_MODE:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif mode == EDIT_MODE:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif mode == PICKUP_POINT_MODE:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif mode == MULTI_SELECT_MODE:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def initContour(self, contours_by_layer):
        """
        Initialize contours from a dictionary: { layer_name: [contour1, contour2, ...] }
        """
        print("in contoureditor.py")
        from API.shared.contour_editor.BezierSegmentManager import Layer
        if not contours_by_layer:
            return

        self.contours = contours_by_layer  # store the dict instead of a flat list

        for layer_name, contours in contours_by_layer.items():
            if contours is None or len(contours) == 0:
                continue

            for cnt in contours:

                bezier_segments = self.manager.contour_to_bezier(cnt)

                for segment in bezier_segments:
                    # Optional: attach layer info to the segment
                    segment.layer = Layer(layer_name,locked=False,visible=True)

                    self.manager.segments.append(segment)

        self.pointsUpdated.emit()

    def toggle_zooming(self):
        self.is_zooming = not self.is_zooming
        if self.is_zooming:
            self.grabGesture(Qt.GestureType.PinchGesture)
            print("Zooming and pinch gesture enabled.")
        else:
            self.ungrabGesture(Qt.GestureType.PinchGesture)
            print("Zooming and pinch gesture disabled.")

    def reset_zoom_flag(self):
        self.is_zooming = False

    def load_image(self, path):
        if path:
            image = QImage(path)
            if image.isNull():
                # print(f"Failed to load image from: {path}")
                image = QImage(1280, 720, QImage.Format.Format_RGB32)
        else:
            image = QImage(1280, 720, QImage.Format.Format_RGB32)
        image.fill(Qt.GlobalColor.white)
        return image



    def handle_gesture_event(self, event):
        # Handle pinch gesture
        pinch = event.gesture(Qt.GestureType.PinchGesture)
        if pinch:
            if pinch.state() == Qt.GestureState.GestureStarted:
                self._initial_scale = self.scale_factor
            elif pinch.state() == Qt.GestureState.GestureUpdated:
                total_scale_factor = pinch.totalScaleFactor()
                center = pinch.centerPoint()
                old_scale = self.scale_factor
                image_point_under_fingers = (center - self.translation) / old_scale
                self.scale_factor = self._initial_scale * total_scale_factor
                self.scale_factor = max(0.1, min(self.scale_factor, 20.0))
                self.translation = center - image_point_under_fingers * self.scale_factor
                self.update()
            elif pinch.state() == Qt.GestureState.GestureFinished:
                pass



    def update_image(self, image_input):
        if isinstance(image_input, str):
            image = QImage(image_input)
            if image.isNull():
                # print(f"Failed to load image from path: {image_input}")
                return
            self.image = image
        elif isinstance(image_input, QImage):
            self.image = image_input
        else:
            print("Unsupported image input type.")
            return
        self.update()

    def event(self, event):
        if event.type() == QEvent.Type.Gesture:
            self.handle_gesture_event(event)
            return True
        return super().event(event)

    def delete_segment(self, seg_index):
        self.manager.delete_segment(seg_index)

    def wheelEvent(self, event):
        self._handle_zoom(event)

    def _handle_zoom(self, event):
        angle = event.angleDelta().y()
        factor = 1.25 if angle > 0 else 0.8

        cursor_pos = event.position()
        cursor_img_pos = (cursor_pos - self.translation) / self.scale_factor

        self.scale_factor *= factor

        # Update translation to zoom towards cursor
        new_cursor_screen_pos = cursor_img_pos * self.scale_factor + self.translation
        self.translation += cursor_pos - new_cursor_screen_pos

        self.update()

    def mousePressEvent(self, event):
        if self.is_zooming:
            self.last_drag_pos = event.position()
            return

        if self.drag_mode_active and event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.last_drag_pos = event.position()
            return

        if not self.is_within_image(event.position()):
            print(f"Position out of image: {event.position()}")
            return

        pos = self.map_to_image_space(event.position())
        print("Mouse pressed at image coords:", pos)

        # Right-click handling
        if event.button() == Qt.MouseButton.RightButton:
            if self.manager.remove_control_point_at(pos):
                self._handle_right_mouse_click()
                return

        elif event.button() == Qt.MouseButton.LeftButton:
            # Handle pickup point mode
            if self.pickup_point_mode_active:
                self.pickup_point = pos
                print(f"Pickup point set at: {pos}")
                self.update()
                return

            # Check for Ctrl modifier or multi-select mode for multi-selection
            ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
            # Also check if TopbarWidget has multi-select mode active
            topbar_multi_select = False
            if hasattr(self, 'parent') and hasattr(self.parent, 'topbar') and hasattr(self.parent.topbar, 'multi_select_mode_active'):
                topbar_multi_select = self.parent.topbar.multi_select_mode_active
            
            multi_select_active = ctrl_pressed or self.multi_select_mode_active or topbar_multi_select

            # ✅ First, check if the click is on an existing anchor or control point
            drag_target = self.manager.find_drag_target(pos)
            
            if drag_target:
                if multi_select_active:
                    # Multi-selection mode: toggle point selection
                    self.toggle_point_selection(drag_target)
                    self.update()
                    return
                else:
                    # Single selection mode: set as single selection and start dragging
                    self.set_single_selection(drag_target)
                    self._handle_left_mouse_dragging(drag_target, pos)
                    print(f"Single selection and dragging point: {drag_target}")
                    return

            # If multi-select mode or Ctrl+Click on empty area, maintain current selections
            if multi_select_active:
                print("Multi-select mode: click on empty area - maintaining selections")
                return

            # Clear all selections when clicking on empty area (without multi-select)
            self.clear_all_selections()

            # ✅ Only if not dragging an existing point, check for segment to add control point
            result = self._handle_add_control_point(pos)
            if result:
                print(f" _handle_add_control_point return result: {result}")
                return  # Control point added successfully

            # ✅ If not dragging or adding control point, check if it's a new anchor point
            # Fallback: add new anchor point
            self.manager.add_point(pos)
            self.update()
            self.pointsUpdated.emit()

    def _handle_add_control_point(self, pos):
        # Get the segment info at the position
        segment_info = self.manager.find_segment_at(pos)
        if segment_info:
            seg_index, line_index = segment_info
            segment = self.manager.get_segments()[seg_index]

            # Check if the line already has a control point, if not, add one
            if line_index >= len(segment.controls) or segment.controls[line_index] is None:
                result = self.manager.add_control_point(seg_index, pos)

                # If the result is False, that means adding the control point was prevented (e.g., due to layer being locked)
                if not result:
                    return False

                # Update and emit signals if control point is successfully added
                self.update()
                self.pointsUpdated.emit()
                return True

        return False

    def _handle_right_mouse_click(self):
        self.selected_point_info = None
        self.update()
        self.pointsUpdated.emit()

    def _handle_left_mouse_dragging(self, drag_target, pos):
        self.dragging_point = drag_target
        self.selected_point_info = drag_target
        self.initial_drag_pos = pos
        self.manager.save_state()
        self.update()

    def set_layer_visibility(self, layer_name, visible):

        if layer_name == "Workpiece":
            layer = self.manager.external_layer
        elif layer_name == "Contour":
            layer = self.manager.contour_layer
        elif layer_name == "Fill":
            layer = self.manager.fill_layer
        else:
            print("Invalid layer: ", layer_name)
            return

        layer.visible = visible

        for idx, segment in enumerate(self.manager.get_segments()):
            if segment.layer.name == layer.name:
                self.manager.set_segment_visibility(idx, visible)

        self.update()  # Redraw after visibility change

    def mouseDoubleClickEvent(self, event):
        pos = event.position()
        target = self.manager.find_drag_target(pos)

        if target and target[0] == 'control':
            role, seg_index, ctrl_idx = target
            self.manager.reset_control_point(seg_index, ctrl_idx)
            self.update()
            self.pointsUpdated.emit()

    #

    def mouseMoveEvent(self, event):
        # Handle panning when in zooming mode
        if self.is_zooming and self.last_drag_pos is not None:
            delta = event.position() - self.last_drag_pos
            self.translation += delta
            self.last_drag_pos = event.position()
            self.pending_drag_update = True
            if not self.drag_timer.isActive():
                self.drag_timer.start()
            return
            
        if self.drag_mode_active and self.last_drag_pos is not None:
            delta = event.position() - self.last_drag_pos
            self.translation += delta
            self.last_drag_pos = event.position()
            self.pending_drag_update = True
            if not self.drag_timer.isActive():
                self.drag_timer.start()
            return

        if self.dragging_point:
            current_pos = self.map_to_image_space(event.position())
            if not self.is_within_image(event.position()):
                return

            delta = current_pos - self.initial_drag_pos
            if abs(delta.x()) > self.drag_threshold or abs(delta.y()) > self.drag_threshold:
                role, seg_index, idx = self.dragging_point
                self.manager.move_point(role, seg_index, idx, self.initial_drag_pos + delta, suppress_save=True)
                self.pending_drag_update = True
                if not self.drag_timer.isActive():
                    self.drag_timer.start()

    def perform_drag_update(self):
        if self.pending_drag_update:
            self.update()
            self.pending_drag_update = False
        else:
            self.drag_timer.stop()

    def mouseReleaseEvent(self, event):
        self.dragging_point = None
        
        # Handle zooming mode release
        if self.is_zooming:
            self.last_drag_pos = None
            self.update()
            return
            
        if self.drag_mode_active:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.last_drag_pos = None

        self.update()

    def addNewSegment(self, layer_name="Contour"):
        print("New segment started.")
        newSegment = self.manager.start_new_segment(layer_name)

        print("Current segments:", self.manager.get_segments())  # Debug print
        self.update()
        self.pointsUpdated.emit()

    def set_image(self, image):
        if image is None:
            return
        height, width, channels = image.shape
        bytes_per_line = channels * width
        fmt = QImage.Format.Format_RGB888 if channels == 3 else QImage.Format.Format_RGBA888
        qimage = QImage(image.data, width, height, bytes_per_line, fmt)
        self.update_image(qimage)



    def map_to_image_space(self, pos):
        print("Mapping to image space:", pos, "Translation:", self.translation, "Scale factor:", self.scale_factor)
        point = (pos - self.translation) / self.scale_factor
        print(f"Mapped point: {point}")
        return point

    def paintEvent(self, event):
        painter = QPainter(self)
        if not painter.isActive():
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        # Apply transformation
        painter.translate(self.translation)
        painter.scale(self.scale_factor, self.scale_factor)

        painter.drawImage(0, 0, self.image)

        for segment in self.manager.get_segments():
            if segment.visible:
                # if segment.get("visible", True):  # Default to True if missing
                self.draw_bezier_segment(painter, segment)

        # Draw pickup point if set
        if self.pickup_point is not None:
            self.draw_pickup_point(painter, self.pickup_point)

        # Draw selection status indicator
        self.draw_selection_status(painter)

        painter.end()

    def get_active_segment_rect(self):
        segment = self.manager.get_active_segment()
        if not segment or not segment.visible:
            return None

        points = segment.points + [pt for pt in segment.controls if pt is not None]
        if not points:
            return None

        min_x = min(p.x() for p in points)
        max_x = max(p.x() for p in points)
        min_y = min(p.y() for p in points)
        max_y = max(p.y() for p in points)

        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def draw_bezier_segment(self, painter, segment):
        points = segment.points
        controls = segment.controls

        # Check if this is the active segment
        is_active = (self.manager.segments.index(segment) == self.manager.active_segment_index)

        if len(points) >= 2:
            # Start path at the first point
            path = QPainterPath()
            path.moveTo(points[0])

            # Loop over the points and controls to create the path
            for i in range(1, len(points)):
                if i - 1 < len(controls) and controls[i - 1] is not None:  # If we have a control point for this segment
                    path.quadTo(controls[i - 1], points[i])  # Draw a quadratic Bézier curve
                else:
                    # If no control points, draw a straight line (this is the fallback)
                    path.lineTo(points[i])

            # Set the color for the path based on the layer (inactive segments will have reduced opacity)
            layer = segment.layer
            color = LAYER_COLORS.get(layer.name, QColor("black"))  # Default layer color

            # Set thickness and opacity based on whether the segment is active or not
            if is_active:
                pen = QPen(color, 2)  # Active segment will have a thicker line
            else:
                # Inactive segments: thinner line and with reduced opacity
                pen = QPen(color, 1)
                pen.setColor(color.lighter(150))  # Slightly lighter color for inactive segments (reduce opacity)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # Smooth ends
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)  # Smooth joins

            # Apply the pen settings
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        # Draw anchor points (points on the curve)
        painter.setPen(QPen(Qt.PenStyle.NoPen))  # No outline for the points
        for i, pt in enumerate(points):
            seg_index = self.manager.segments.index(segment)
            
            # Check if this point is in multi-selection
            is_multi_selected = self.is_point_selected('anchor', seg_index, i)
            
            # Check backward compatibility with single selection
            is_single_selected = (
                self.selected_point_info == ('anchor', seg_index, i)
            )

            # Set color and size for selected points
            if is_multi_selected and len(self.selected_points_list) > 1:
                #Multi-selection:
                color = QColor(0x67, 0x50, 0xA4)  # Purple #6750A4
                size = 6
            elif is_single_selected or is_multi_selected:
                # Single selection: use green
                color = Qt.GlobalColor.green
                size = 6
            else:
                # Unselected: use blue
                color = Qt.GlobalColor.blue
                size = 5
                
            painter.setBrush(QBrush(color))
            painter.drawEllipse(pt, size, size)

        # Draw control points (if available)
        for i, pt in enumerate(controls):
            if pt is None:
                continue  # Skip invalid control points
                
            seg_index = self.manager.segments.index(segment)
            
            # Check if this control point is in multi-selection
            is_multi_selected = self.is_point_selected('control', seg_index, i)
            
            # Check backward compatibility with single selection
            is_single_selected = (
                self.selected_point_info == ('control', seg_index, i)
            )
            
            # Set color and size for selected control points
            if is_multi_selected and len(self.selected_points_list) > 1:
                # Multi-selection: use orange/yellow for multiple selected points
                color = QColor(0x67, 0x50, 0xA4)  # Purple #6750A4
                size = 8
            elif is_single_selected or is_multi_selected:
                # Single selection: use green
                color = Qt.GlobalColor.green
                size = 8
            else:
                # Unselected: use red
                color = Qt.GlobalColor.red
                size = 5
                
            painter.setBrush(QBrush(color))
            painter.drawEllipse(pt, size, size)

        # Optionally, draw lines connecting anchor points to control points (debugging or visualization)
        painter.setPen(QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))
        for i in range(1, len(points)):
            if i - 1 < len(controls):
                ctrl = controls[i - 1]
                if ctrl is not None:
                    painter.drawLine(points[i - 1], ctrl)
                    painter.drawLine(ctrl, points[i])

    def draw_pickup_point(self, painter, point):
        """Draw the pickup point as a distinctive visual marker"""
        # painter.setPen(QPen(QColor(0x67, 0x50, 0xA4)))
        painter.setBrush(QBrush(QColor(0x67, 0x50, 0xA4)))  # Purple color
        
        # Draw a larger circle for the pickup point
        painter.drawEllipse(point, 10, 10)
        
        # Draw a crosshair inside the circle
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(int(point.x() - 8), int(point.y()), int(point.x() + 8), int(point.y()))
        painter.drawLine(int(point.x()), int(point.y() - 8), int(point.x()), int(point.y() + 8))

    def toggle_point_selection(self, drag_target):
        """Toggle selection state of a point for multi-selection"""
        if not drag_target:
            return
            
        role, seg_index, point_index = drag_target
        selection_dict = {
            'role': role,
            'seg_index': seg_index,
            'point_index': point_index
        }
        
        # Check if this point is already selected
        for i, selected in enumerate(self.selected_points_list):
            if (selected['role'] == role and 
                selected['seg_index'] == seg_index and 
                selected['point_index'] == point_index):
                # Point is selected, remove it
                del self.selected_points_list[i]
                print(f"Deselected point: {selection_dict}")
                return
        
        # Point is not selected, add it
        self.selected_points_list.append(selection_dict)
        print(f"Selected point: {selection_dict}")
    
    def clear_all_selections(self):
        """Clear all point selections"""
        self.selected_points_list.clear()
        self.selected_point_info = None
        print("Cleared all selections")
    
    def set_single_selection(self, drag_target):
        """Set a single point selection (clears others)"""
        self.clear_all_selections()
        if drag_target:
            role, seg_index, point_index = drag_target
            self.selected_point_info = drag_target  # Maintain backward compatibility
            self.selected_points_list.append({
                'role': role,
                'seg_index': seg_index,
                'point_index': point_index
            })
            print(f"Single selection set: {drag_target}")
    
    def is_point_selected(self, role, seg_index, point_index):
        """Check if a specific point is selected"""
        for selected in self.selected_points_list:
            if (selected['role'] == role and 
                selected['seg_index'] == seg_index and 
                selected['point_index'] == point_index):
                return True
        return False
    
    def get_selected_points_count(self):
        """Get the number of currently selected points"""
        return len(self.selected_points_list)
    
    def draw_selection_status(self, painter):
        """Draw selection status indicator in the top-right corner"""
        selected_count = self.get_selected_points_count()
        if selected_count <= 1:
            return  # Don't show indicator for single or no selection
            
        # Reset painter transformations for UI overlay
        painter.resetTransform()
        
        # Set up text
        status_text = f"{selected_count} points selected"
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        # Calculate text size and position
        text_rect = painter.fontMetrics().boundingRect(status_text)
        padding = 8
        margin = 10
        
        # Position in top-right corner
        x = self.width() - text_rect.width() - padding * 2 - margin
        y = margin
        
        # Draw background
        bg_rect = QRectF(x - padding, y, text_rect.width() + padding * 2, text_rect.height() + padding)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(103, 80, 164, 200)))  # Semi-transparent #6750A4

        painter.drawRoundedRect(bg_rect, 4, 4)
        
        # Draw text
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(int(x), int(y + text_rect.height()), status_text)

    def save_robot_path_dict_to_txt(self, filename="robot_path_dict.txt", samples_per_segment=5):
        robot_path_dict = self.manager.to_wp_data(samples_per_segment)
        try:
            with open(filename, 'w') as f:
                for segment_name, path in robot_path_dict.items():
                    f.write(f"Segment: {segment_name}\n")
                    for pt in path:
                        f.write(f"{pt.x():.3f}, {pt.y():.3f}\n")
                    f.write("\n")  # Add a blank line between segments
            print(f"Saved path to {filename}")
        except Exception as e:
            print(f"Error saving path: {e}")

        return robot_path_dict

    def save_robot_path_to_txt(self, filename="robot_path.txt", samples_per_segment=5):
        path = self.manager.get_robot_path(samples_per_segment)
        try:
            with open(filename, 'w') as f:
                for pt in path:
                    f.write(f"{pt.x():.3f}, {pt.y():.3f}\n")
            print(f"Saved path to {filename}")
        except Exception as e:
            print(f"Error saving path: {e}")

    def plot_robot_path(self, filename="robot_path.txt"):
        try:
            with open(filename, 'r') as f:
                coords = [tuple(map(float, line.strip().split(','))) for line in f if ',' in line]

            # Remove duplicate points
            unique_coords = list(set(coords))
            unique_coords.sort(key=coords.index)  # Preserve the original order

            x_vals, y_vals = zip(*unique_coords)
            total_points = len(unique_coords)  # Count the total number of unique points

            plt.figure(figsize=(12.8, 7.2))
            plt.plot(x_vals, y_vals, 'b-', label="Robot Path")  # Plot the path
            plt.scatter(x_vals, y_vals, color='red', label=f"Points ({total_points})")  # Plot the points
            plt.gca().invert_yaxis()
            plt.xlim(0, self.width())
            plt.ylim(self.height(), 0)
            plt.title(f"Robot Path Visualization (Total Points: {total_points})")  # Include total points in the title
            plt.xlabel("X")
            plt.ylabel("Y")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Failed to plot path: {e}")

    def is_within_image(self, pos: QPointF) -> bool:
        image_width = self.image.width()
        image_height = self.image.height()
        img_pos = self.map_to_image_space(pos)
        return 0 <= img_pos.x() < image_width and 0 <= img_pos.y() < image_height

    def set_layer_locked(self, layer_name, locked):
        self.manager.set_layer_locked(layer_name, locked)
        print("Layer lock state updated:", layer_name, locked)
    
    def show_global_settings(self):
        from pl_ui.contour_editor.GlobalSettingsDialog import GlobalSettingsDialog
        if hasattr(self, 'point_manager_widget') and self.point_manager_widget:
            dialog = GlobalSettingsDialog(self.point_manager_widget, parent=self)
            dialog.exec()
        else:
            print("Point manager widget not found")
    
    def keyPressEvent(self, event):
        from PyQt6.QtCore import Qt
        if event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.show_global_settings()
        else:
            super().keyPressEvent(event)


import sys
import threading
from PyQt6.QtWidgets import (
    QFrame, QWidget, QHBoxLayout, QVBoxLayout, QApplication,
    QTabWidget
)
from PyQt6.QtCore import QFile, QTextStream

# from GlueDispensingApplication.vision.VisionService import VisionServiceSingleton
from pl_ui.contour_editor.PointManagerWidget import PointManagerWidget
# from NewContourEditor.PointManager import PointManagerWidget
from pl_ui.ui.widgets.CreateWorkpieceForm import CreateWorkpieceForm
from pl_ui.contour_editor.TopbarWidget import TopBarWidget
# from .TopbarWidget import TopBarWidget


class MainApplicationFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # self.visionSystem = VisionServiceSingleton.get_instance()

        # State management
        self.current_view = "point_manager"  # "point_manager" or "create_workpiece"

        # # Start the vision system thread
        # threading.Thread(target=self.runCameraFeed, daemon=True).start()

        self.initUI()

    # def runCameraFeed(self):
    #     while True:
    #         self.visionSystem.run()

    def initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        # Bezier editor on the left
        self.contourEditor = ContourEditor(None, image_path="imageDebug.png")

        # Top bar widget
        self.topbar = TopBarWidget(self.contourEditor, None,zigzag_callback=self.generateLineGridPattern,offset_callback=self.shrink)
        mainLayout.addWidget(self.topbar)

        # Horizontal layout for the main content
        horizontal_widget = QWidget()
        horizontalLayout = QHBoxLayout(horizontal_widget)
        horizontalLayout.setContentsMargins(0, 0, 0, 0)

        horizontalLayout.addWidget(self.contourEditor, stretch=4)

        # Create the right panel widgets
        self.pointManagerWidget = PointManagerWidget(self.contourEditor,self.parent)
        self.topbar.point_manager = self.pointManagerWidget
        self.contourEditor.point_manager_widget = self.pointManagerWidget
        self.pointManagerWidget.setFixedWidth(400)

        self.createWorkpieceForm = CreateWorkpieceForm(parent=self)
        # self.createWorkpieceForm.apply_stylesheet()
        self.createWorkpieceForm.setFixedWidth(350)
        self.createWorkpieceForm.hide()  # Initially hidden

        # Add point manager to layout (initially visible)
        horizontalLayout.addWidget(self.pointManagerWidget, stretch=1)
        horizontalLayout.addWidget(self.createWorkpieceForm, stretch=1)

        # Set up save button callback to switch views
        self.topbar.set_save_button_callback(self.on_first_save_clicked)
        self.topbar.onStartCallback = self.onStart
        # Add the horizontal widget to the main layout
        mainLayout.addWidget(horizontal_widget)

    def set_create_workpiece_for_on_submit_callback(self, callback):
        """
        Set the callback for when the create workpiece button is clicked.
        This allows the main application to handle the creation of a workpiece.
        """
        self.createWorkpieceForm.onSubmitCallBack = callback
        print("Set create workpiece callback in main application frame.")

    def shrink(self):
        from pl_ui.contour_editor.utils import shrink_contour_points
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QInputDialog
        from PyQt6.QtCore import Qt
        
        # First, ask user to select layer type with custom dialog
        class LayerSelectionDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Layer Selection for Shrink")
                self.setModal(True)
                self.setFixedSize(300, 150)
                
                layout = QVBoxLayout(self)
                
                # Label
                label = QLabel("Select layer for shrunk contour:")
                label.setStyleSheet("color: #4A2C4A; font-size: 12px; font-weight: bold;")
                layout.addWidget(label)
                
                # Combo box
                self.combo_box = QComboBox()
                self.combo_box.addItems(["Contour", "Fill"])
                self.combo_box.setStyleSheet("""
                    QComboBox {
                        background-color: #F8F4F8;
                        color: #4A2C4A;
                        border: 2px solid #B19CD9;
                        padding: 5px;
                        font-size: 12px;
                        border-radius: 4px;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 5px solid #4A2C4A;
                    }
                    QComboBox QAbstractItemView {
                        background-color: white;
                        color: #4A2C4A;
                        selection-background-color: #B19CD9;
                    }
                    QComboBox:focus {
                        border: 2px solid #8B4E9B;
                    }
                """)
                layout.addWidget(self.combo_box)
                
                # Buttons
                button_layout = QHBoxLayout()
                self.ok_button = QPushButton("OK")
                self.cancel_button = QPushButton("Cancel")
                
                self.ok_button.setStyleSheet("""
                    QPushButton {
                        background-color: #8B4E9B;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        font-size: 12px;
                        border-radius: 4px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #7A4A8A;
                    }
                    QPushButton:pressed {
                        background-color: #6A3A7A;
                    }
                """)
                
                self.cancel_button.setStyleSheet("""
                    QPushButton {
                        background-color: #B19CD9;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        font-size: 12px;
                        border-radius: 4px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #A085D1;
                    }
                    QPushButton:pressed {
                        background-color: #9075C1;
                    }
                """)
                
                self.ok_button.clicked.connect(self.accept)
                self.cancel_button.clicked.connect(self.reject)
                
                button_layout.addWidget(self.ok_button)
                button_layout.addWidget(self.cancel_button)
                layout.addLayout(button_layout)
                
                # Set dialog background
                self.setStyleSheet("QDialog { background-color: white; }")
            
            def get_selected_layer(self):
                return self.combo_box.currentText()

        # Show layer selection dialog
        layer_dialog = LayerSelectionDialog(self)
        if layer_dialog.exec() != QDialog.DialogCode.Accepted:
            print("Shrink cancelled by user.")
            return
        
        selected_layer = layer_dialog.get_selected_layer()

        # Create styled input dialog for shrink amount
        def create_styled_input_dialog(parent, title, label, value, min_val, max_val):
            dialog = QInputDialog(parent)
            dialog.setWindowTitle(title)
            dialog.setLabelText(label)
            dialog.setIntValue(value)
            dialog.setIntMinimum(min_val)
            dialog.setIntMaximum(max_val)
            
            # Apply white and purple styling
            dialog.setStyleSheet("""
                QInputDialog {
                    background-color: white;
                    color: #4A2C4A;
                }
                QLabel {
                    color: #4A2C4A;
                    font-size: 12px;
                    font-weight: bold;
                }
                QSpinBox {
                    background-color: #F8F4F8;
                    color: #4A2C4A;
                    border: 2px solid #B19CD9;
                    padding: 5px;
                    font-size: 12px;
                    border-radius: 4px;
                }
                QSpinBox:focus {
                    border: 2px solid #8B4E9B;
                }
                QPushButton {
                    background-color: #8B4E9B;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-size: 12px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #7A4A8A;
                }
                QPushButton:pressed {
                    background-color: #6A3A7A;
                }
            """)
            
            return dialog.exec(), dialog.intValue()

        # Get shrink amount
        ok, shrink_amount = create_styled_input_dialog(self, "Shrink Amount", "Enter shrink value in mm:", 5, 1, 50)
        if not ok:
            print("Shrink cancelled by user.")
            return

        print(f"Shrinking contour by: {shrink_amount} to layer: {selected_layer}")

        external_segments = [s for s in self.contourEditor.manager.get_segments() if
                             getattr(s.layer, "name", "") == "Workpiece"]
        if not external_segments:
            print("No Workpiece contour found.")
            return

        contour = external_segments[0]
        contour_points = np.array([(pt.x(), pt.y()) for pt in contour.points])
        if contour_points.size == 0:
            print("Workpiece contour has no points.")
            return
        if contour_points.shape[0] < 3:
            print("Contour has fewer than 3 points — can't shrink properly.")
            return

        if shrink_amount <= 0:
            print("Shrink amount must be positive.")
            new_contour_points = contour_points
        else:
            new_contour_points = shrink_contour_points(contour_points, shrink_amount)
            if new_contour_points is None or len(new_contour_points) < 2:
                print("Shrink amount too large — polygon disappeared or invalid result!")
                return

        for i in range(len(new_contour_points) - 1):
            p1 = new_contour_points[i]
            p2 = new_contour_points[i + 1]
            qpoints = [QPointF(p1[0], p1[1]), QPointF(p2[0], p2[1])]
            segment = self.contourEditor.manager.create_segment(qpoints, layer_name=selected_layer)
            self.contourEditor.manager.segments.append(segment)

        self.contourEditor.update()
        self.pointManagerWidget.refresh_points()
        print(f"Added shrunk contour inward by {shrink_amount} units as new segments in {selected_layer} layer.")

    def generateLineGridPattern(self):
        """
        Generate zig-zag lines aligned to the Workpiece contour using minimum area bounding box orientation.
        """
        from PyQt6.QtWidgets import QInputDialog
        from PyQt6.QtCore import QPointF
        import numpy as np
        import cv2
        from shapely.geometry import LineString, Polygon
        from pl_ui.contour_editor.utils import zigZag

        # Ask user to select layer type with custom dialog for better styling
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        
        class LayerSelectionDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Layer Selection")
                self.setModal(True)
                self.setFixedSize(300, 150)
                
                layout = QVBoxLayout(self)
                
                # Label
                label = QLabel("Select layer type for zigzag pattern:")
                label.setStyleSheet("color: black; font-size: 12px;")
                layout.addWidget(label)
                
                # Combo box
                self.combo_box = QComboBox()
                self.combo_box.addItems(["Contour", "Fill"])
                self.combo_box.setStyleSheet("""
                    QComboBox {
                        background-color: white;
                        color: black;
                        border: 1px solid gray;
                        padding: 5px;
                        font-size: 12px;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                    QComboBox::down-arrow {
                        image: none;
                        border-left: 5px solid transparent;
                        border-right: 5px solid transparent;
                        border-top: 5px solid black;
                    }
                    QComboBox QAbstractItemView {
                        background-color: white;
                        color: black;
                        selection-background-color: lightblue;
                    }
                """)
                layout.addWidget(self.combo_box)
                
                # Buttons
                button_layout = QHBoxLayout()
                self.ok_button = QPushButton("OK")
                self.cancel_button = QPushButton("Cancel")
                
                self.ok_button.setStyleSheet("""
                    QPushButton {
                        background-color: #8B4E9B;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        font-size: 12px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #7A4A8A;
                    }
                """)
                
                self.cancel_button.setStyleSheet("""
                    QPushButton {
                        background-color: #B19CD9;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        font-size: 12px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #A085D1;
                    }
                """)
                
                self.ok_button.clicked.connect(self.accept)
                self.cancel_button.clicked.connect(self.reject)
                
                button_layout.addWidget(self.ok_button)
                button_layout.addWidget(self.cancel_button)
                layout.addLayout(button_layout)
                
                # Set dialog background
                self.setStyleSheet("QDialog { background-color: #f0f0f0; }")
            
            def get_selected_layer(self):
                return self.combo_box.currentText()
        
        dialog = LayerSelectionDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            print("Zig-zag pattern generation cancelled by user.")
            return
        
        selected_layer = dialog.get_selected_layer()

        # first clear all the segments in the selected layer
        self.contourEditor.manager.segments = [s for s in self.contourEditor.manager.get_segments() if
                                               getattr(s.layer, "name", "") != selected_layer]
        # also update the ui to reflect this
        self.contourEditor.update()

        # Create custom styled QInputDialog for grid spacing
        def create_styled_input_dialog(parent, title, label, value, min_val, max_val):
            dialog = QInputDialog(parent)
            dialog.setWindowTitle(title)
            dialog.setLabelText(label)
            dialog.setIntValue(value)
            dialog.setIntMinimum(min_val)
            dialog.setIntMaximum(max_val)
            
            # Apply white and purple styling
            dialog.setStyleSheet("""
                QInputDialog {
                    background-color: white;
                    color: #4A2C4A;
                }
                QLabel {
                    color: #4A2C4A;
                    font-size: 12px;
                    font-weight: bold;
                }
                QSpinBox {
                    background-color: #F8F4F8;
                    color: #4A2C4A;
                    border: 2px solid #B19CD9;
                    padding: 5px;
                    font-size: 12px;
                    border-radius: 4px;
                }
                QSpinBox:focus {
                    border: 2px solid #8B4E9B;
                }
                QPushButton {
                    background-color: #8B4E9B;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-size: 12px;
                    border-radius: 4px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #7A4A8A;
                }
                QPushButton:pressed {
                    background-color: #6A3A7A;
                }
            """)
            
            return dialog.exec(), dialog.intValue()
        
        ok, spacing = create_styled_input_dialog(self, "Line Grid Spacing", "Enter value in mm:", 20, 1, 1000)
        if not ok:
            print("Zig-zag pattern generation cancelled by user.")
            return

        ok, shrink_offset = create_styled_input_dialog(self, "Shrink", "Enter value in mm (0 for none):", 0, 0, 50)

        if not ok:
            shrink_offset=0

        if shrink_offset > 0:
            # Shrink the contour first
            external_segments = [s for s in self.contourEditor.manager.get_segments() if
                                 getattr(s.layer, "name", "") == "Workpiece"]
            if not external_segments:
                print("No Workpiece contour found.")
                return

            contour = external_segments[0]
            contour_points = np.array([(pt.x(), pt.y()) for pt in contour.points])
            if contour_points.size == 0:
                print("Workpiece contour has no points.")
                return
            if contour_points.shape[0] < 3:
                print("Contour has fewer than 3 points — can't shrink properly.")
                return

            new_contour_points = shrink_contour_points(contour_points, shrink_offset)
            if new_contour_points is None or len(new_contour_points) < 2:
                print("Shrink amount too large — polygon disappeared or invalid result!")
                return
            contour_points = new_contour_points.astype(np.float32)
        else:

            # Get Workpiece contour
            external_segments = [s for s in self.contourEditor.manager.get_segments() if
                                 getattr(s.layer, "name", "") == "Workpiece"]
            if not external_segments:
                print("No Workpiece contour found.")
                return

            contour = external_segments[0]
            contour_points = np.array([(pt.x(), pt.y()) for pt in contour.points])
            if contour_points.size == 0:
                print("Workpiece contour has no points.")
                return

            # Ensure contour is not empty and convert to float32 for OpenCV
            if contour_points.shape[0] < 3:
                print("Contour has fewer than 3 points — can't compute minAreaRect.")
                return

            contour_points = contour_points.astype(np.float32)

        # Generate zig-zag points
        zigzag_points = zigZag(contour_points, spacing)

        # Create line segments
        if selected_layer == "Fill":
            # For Fill layer: Create one continuous segment with all zigzag points
            all_qpoints = []
            for i in range(0, len(zigzag_points) - 1, 2):
                p1 = zigzag_points[i]
                p2 = zigzag_points[i + 1]
                if (i // 2) % 2 == 0:
                    # Left to right
                    all_qpoints.append(QPointF(p1[0], p1[1]))
                    all_qpoints.append(QPointF(p2[0], p2[1]))
                else:
                    # Right to left
                    all_qpoints.append(QPointF(p2[0], p2[1]))
                    all_qpoints.append(QPointF(p1[0], p1[1]))
            
            # Create one big segment with all points
            if all_qpoints:
                segment = self.contourEditor.manager.create_segment(all_qpoints, layer_name=selected_layer)
                self.contourEditor.manager.segments.append(segment)
        else:
            # For Contour layer: Create individual segments with alternating directions (left-right, right-left)
            for i in range(0, len(zigzag_points) - 1, 2):
                p1 = zigzag_points[i]
                p2 = zigzag_points[i + 1]
                if (i // 2) % 2 == 0:
                    qpoints = [QPointF(p1[0], p1[1]), QPointF(p2[0], p2[1])]
                else:
                    qpoints = [QPointF(p2[0], p2[1]), QPointF(p1[0], p1[1])]

                segment = self.contourEditor.manager.create_segment(qpoints, layer_name=selected_layer)
                self.contourEditor.manager.segments.append(segment)

        self.contourEditor.update()
        self.pointManagerWidget.refresh_points()
        print("Generated zig-zag grid aligned to Workpiece contour.")

    def on_first_save_clicked(self):
        """Handle the first save button click - switch from point manager to create workpiece form"""
        if self.current_view == "point_manager":
            # Hide point manager and show create workpiece form
            self.pointManagerWidget.hide()
            # self.createWorkpieceForm.show()
            # self.createWorkpieceForm.raise_()
            self.createWorkpieceForm.toggle()
            # Update the save button callback to handle workpiece saving
            self.topbar.set_save_button_callback(self.on_workpiece_save_clicked)
            self.current_view = "create_workpiece"

            print("Switched to Create Workpiece form")

    def onStart(self):
        from API.shared.workpiece.Workpiece import WorkpieceField
        from GlueDispensingApplication.workpiece.Workpiece import Workpiece,WorkpieceField


        mock_data = {
            WorkpieceField.WORKPIECE_ID.value: "WP123",
            WorkpieceField.NAME.value: "Test Workpiece",
            WorkpieceField.DESCRIPTION.value: "Sample description",
            WorkpieceField.OFFSET.value: "10,20,30",
            WorkpieceField.HEIGHT.value: "50",
            WorkpieceField.GLUE_QTY.value: "100",
            WorkpieceField.SPRAY_WIDTH.value: "5",
            WorkpieceField.TOOL_ID.value: "0",
            WorkpieceField.GRIPPER_ID.value: "0",
            WorkpieceField.GLUE_TYPE.value: "Type A",
            WorkpieceField.PROGRAM.value: "Trace",
            WorkpieceField.MATERIAL.value: "Material1",
            WorkpieceField.CONTOUR_AREA.value: "1000",
        }

        wp_contours_data = self.contourEditor.manager.to_wp_data(samples_per_segment=5)
        print("Workpiece contours data:", wp_contours_data)
        
        def has_valid_contours(contour_list):
            """Check if contour list has valid contour data (not empty arrays)"""
            if not contour_list or len(contour_list) == 0:
                return False
            
            for item in contour_list:
                if isinstance(item, dict) and 'contour' in item:
                    contour = item['contour']
                    # Check if contour array has actual points (not empty)
                    if contour.size > 0 and len(contour) > 0:
                        return True
            return False
        
        sprayPatternsDict = {
            "Contour": [],
            "Fill": []
        }

        contour_data = wp_contours_data.get('Contour', [])
        fill_data = wp_contours_data.get('Fill', [])
        
        sprayPatternsDict['Contour'] = contour_data
        sprayPatternsDict['Fill'] = fill_data

        # Check if either Contour or Fill has valid data
        has_contour = has_valid_contours(contour_data)
        has_fill = has_valid_contours(fill_data)
        
        if not has_contour and not has_fill:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Spray Pattern", "No valid contour or fill patterns found!")
            return

        mock_data[WorkpieceField.SPRAY_PATTERN.value] = sprayPatternsDict
        mock_data[WorkpieceField.CONTOUR.value] = wp_contours_data.get('Workpiece')
        
        # Add pickup point if set
        if self.contourEditor.pickup_point is not None:
            pickup_point_str = f"{self.contourEditor.pickup_point.x():.2f},{self.contourEditor.pickup_point.y():.2f}"
            mock_data["pickup_point"] = pickup_point_str
            print(f"Pickup point included: {pickup_point_str}")
        else:
            print("No pickup point set")
        
        wp = Workpiece.fromDict(mock_data)
        print("Workpiece created:", wp)
        print("Start button pressed: CONTOUR EDITOR " )
        self.parent.controller.handleExecuteFromGallery(wp)

    def on_workpiece_save_clicked(self):
        """Handle the second save button click - save the workpiece"""
        # Pass pickup point data to the form before submitting
        if self.contourEditor.pickup_point is not None:
            pickup_point_str = f"{self.contourEditor.pickup_point.x():.2f},{self.contourEditor.pickup_point.y():.2f}"
            # Store pickup point in the form's data
            self.createWorkpieceForm.pickup_point = pickup_point_str
            print(f"Pickup point passed to form: {pickup_point_str}")
        else:
            # Clear pickup point if none is set
            self.createWorkpieceForm.pickup_point = None
            print("No pickup point set, clearing form attribute")
        
        # Call the workpiece form's submit method
        self.createWorkpieceForm.onSubmit()
        print("Workpiece saved!")

        # Optionally, you could reset back to point manager or keep the form
        # For now, we'll keep the create workpiece form visible

    def set_image(self, image):
        self.contourEditor.set_image(image)

    def init_contours(self, contours):
        print("in contour editor.py")
        self.contourEditor.initContour(contours)

    def resizeEvent(self, event):
        """Resize content and side menu dynamically."""
        super().resizeEvent(event)
        new_width = self.width()

        # Adjust icon sizes of the sidebar buttons
        icon_size = int(new_width * 0.05)  # 5% of the new window width
        for button in self.topbar.buttons:
            button.setIconSize(QSize(icon_size, icon_size))

        if hasattr(self.createWorkpieceForm, 'buttons'):
            for button in self.createWorkpieceForm.buttons:
                button.setIconSize(QSize(icon_size, icon_size))

        # Resize the icons in the labels
        if hasattr(self.createWorkpieceForm, 'icon_widgets'):
            for label, original_pixmap in self.createWorkpieceForm.icon_widgets:
                scaled_pixmap = original_pixmap.scaled(
                    int(icon_size / 2), int(icon_size / 2),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                label.setPixmap(scaled_pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load and apply stylesheet
    # stylesheetPath = "D:/GitHub/Cobot-Glue-Nozzle/pl_gui/styles.qss"
    # file = QFile(stylesheetPath)
    # if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
    #     stream = QTextStream(file)
    #     stylesheet = stream.readAll()
    #     file.close()
    #     app.setStyleSheet(stylesheet)

    main_window = QWidget()
    layout = QVBoxLayout(main_window)
    app_frame = MainApplicationFrame()
    layout.addWidget(app_frame)
    main_window.setGeometry(100, 100, 1600, 800)
    main_window.setWindowTitle("Glue Dispensing Application")
    main_window.show()
    sys.exit(app.exec())
