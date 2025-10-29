import os
import sys
from types import SimpleNamespace

from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout,
    QPushButton, QComboBox, QSizePolicy, QLabel
)

# --- Resource Paths ---
RESOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
HIDE_ICON = os.path.join(RESOURCE_DIR, "hide.png")
SHOW_ICON = os.path.join(RESOURCE_DIR, "show.png")
BIN_ICON = os.path.join(RESOURCE_DIR, "BIN_BUTTON_SQUARE.png")
PLUS_ICON = os.path.join(RESOURCE_DIR, "PLUS_BUTTON.png")
LOCK_ICON = os.path.join(RESOURCE_DIR, "locked.png")
UNLOCK_ICON = os.path.join(RESOURCE_DIR, "unlocked.png")
ACTIVE_ICON = os.path.join(RESOURCE_DIR, "active.png")
INACTIVE_ICON = os.path.join(RESOURCE_DIR, "inactive.png")
DROPDOWN_OPEN_ICON = os.path.join(RESOURCE_DIR, "dropdown_open.png")


class SegmentButtonsAndComboWidget(QWidget):
    # Define custom signals
    visibility_toggled = pyqtSignal(bool)  # Emits the visibility state
    activated = pyqtSignal()
    deleted = pyqtSignal()
    settings_clicked = pyqtSignal()
    layer_changed = pyqtSignal(str)  # Emits the new layer name

    def __init__(self, seg_index, segment, layer_name):
        super().__init__()

        self.segment = segment
        self.seg_index = seg_index

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Create segment index label with precise width calculation
        self.index_label = self._create_precise_sized_label(f"S{seg_index}", seg_index)
        layout.addWidget(self.index_label)

        # Create buttons and connect to signals
        self.visibility_btn = self._create_visibility_button()
        layout.addWidget(self.visibility_btn)

        self.active_btn = self._create_icon_button(
            ACTIVE_ICON if getattr(segment, "is_active", False) else INACTIVE_ICON,
            "Set as active segment"
        )
        self.active_btn.clicked.connect(self.activated.emit)
        layout.addWidget(self.active_btn)
        self.active_button = self.active_btn

        self.delete_btn = self._create_icon_button(
            BIN_ICON, "Delete this segment"
        )
        self.delete_btn.clicked.connect(self.deleted.emit)
        layout.addWidget(self.delete_btn)

        self.settings_btn = QPushButton("S")
        self.settings_btn.setToolTip("Segment settings")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(self.settings_btn)

        self.combo_box = QComboBox()
        self.combo_box.addItems(["External", "Contour", "Fill"])
        self.combo_box.setCurrentText(layer_name)
        self.combo_box.setFixedHeight(40)
        self.combo_box.setMinimumWidth(100)
        self.combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_box.currentTextChanged.connect(self.layer_changed.emit)
        layout.addWidget(self.combo_box)

        layout.addStretch()

    def _create_precise_sized_label(self, text, seg_index):
        """Create a label with precise width calculation for consistent alignment"""
        label = QLabel(text)
        label.setToolTip(f"Segment index: {seg_index}")

        # Apply style first to get accurate measurements
        label.setStyleSheet("text-align: left; padding-left: 10px;")

        # Calculate text width using font metrics
        font_metrics = label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(text)

        # Calculate width based on expected maximum segment count
        # This ensures consistent alignment even with varying segment numbers
        max_expected_digits = 3  # Supports up to S999
        max_text = "S" + "9" * (max_expected_digits - 1)
        max_text_width = font_metrics.horizontalAdvance(max_text)

        # Use the larger of actual text width or consistent width
        padding = 20  # Left padding + margins
        consistent_width = max_text_width + padding
        actual_width = text_width + padding

        # Choose between consistent width (for alignment) or actual width (for space efficiency)
        # Uncomment the one you prefer:

        # Option 1: Consistent width for perfect alignment
        final_width = consistent_width

        # Option 2: Actual width for space efficiency
        # final_width = max(40, actual_width)

        label.setFixedWidth(final_width)
        label.setFixedHeight(40)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        return label

    def _create_icon_button(self, icon_path, tooltip):
        """Create an icon button without callback parameter"""
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(32, 32))
        button.setToolTip(tooltip)
        button.setFixedSize(40, 40)
        return button

    def _create_visibility_button(self):
        """Create visibility toggle button and connect to signal"""
        button = QPushButton()
        button.setCheckable(True)
        is_visible = getattr(self.segment, "visible", True)
        button.setChecked(is_visible)
        button.setIcon(QIcon(HIDE_ICON if is_visible else SHOW_ICON))
        button.setIconSize(QSize(32, 32))
        button.setToolTip("Toggle segment visibility")
        button.setFixedSize(40, 40)
        button.clicked.connect(lambda: self._toggle_visibility(button))
        return button

    def _toggle_visibility(self, button):
        """Handle visibility toggle and emit signal"""
        is_visible = button.isChecked()
        button.setIcon(QIcon(HIDE_ICON if is_visible else SHOW_ICON))
        self.visibility_toggled.emit(is_visible)

    def update_active_state(self, is_active):
        """Update the active button icon based on state"""
        icon_path = ACTIVE_ICON if is_active else INACTIVE_ICON
        self.active_btn.setIcon(QIcon(icon_path))


# --- Testing ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    segment = SimpleNamespace(visible=True, is_active=False)
    layer_name = "Contour"

    # Create the widget without callbacks
    widget = SegmentButtonsAndComboWidget(
        seg_index=0,
        segment=segment,
        layer_name=layer_name
    )

    # Connect to the signals
    widget.visibility_toggled.connect(lambda visible: print(f"Visibility toggled: {visible}"))
    widget.activated.connect(lambda: print("Activated"))
    widget.deleted.connect(lambda: print("Deleted"))
    widget.settings_clicked.connect(lambda: print("Settings opened"))
    widget.layer_changed.connect(lambda layer: print(f"Layer changed to: {layer}"))

    widget.show()
    sys.exit(app.exec())