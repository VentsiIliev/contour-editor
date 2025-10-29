from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSizePolicy, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtCore import Qt
from API.shared.settings.conreateSettings.enums.GlueSettingKey import GlueSettingKey
from API.shared.settings.conreateSettings.enums.RobotSettingKey import RobotSettingKey
# import qt DoubleSpinBox
from PyQt6.QtWidgets import QDoubleSpinBox
from pl_ui.ui.widgets.virtualKeyboard.VirtualKeyboard import FocusDoubleSpinBox
import json
import os
default_settings = {
    GlueSettingKey.SPRAY_WIDTH.value: "10",
    GlueSettingKey.SPRAYING_HEIGHT.value: "0",
    GlueSettingKey.FAN_SPEED.value: "100",
    GlueSettingKey.TIME_BETWEEN_GENERATOR_AND_GLUE.value: "1",
    GlueSettingKey.MOTOR_SPEED.value: "500",
    GlueSettingKey.REVERSE_DURATION.value: "0.5",
    GlueSettingKey.SPEED_REVERSE.value: "3000",
    GlueSettingKey.RZ_ANGLE.value: "0",
    GlueSettingKey.GLUE_TYPE.value: "Type a",
    GlueSettingKey.GENERATOR_TIMEOUT.value: "5",
    GlueSettingKey.TIME_BEFORE_MOTION.value: "0.1",
    GlueSettingKey.TIME_BEFORE_STOP.value: "1.0",
    GlueSettingKey.REACH_START_THRESHOLD.value: "1.0",
    GlueSettingKey.REACH_END_THRESHOLD.value: "30.0",
    GlueSettingKey.GLUE_SPEED_COEFFICIENT.value: "5",
    GlueSettingKey.GLUE_ACCELERATION_COEFFICIENT.value: "0",
    GlueSettingKey.INITIAL_RAMP_SPEED_DURATION.value: "1.0",
    GlueSettingKey.INITIAL_RAMP_SPEED.value: "5000",
    GlueSettingKey.REVERSE_RAMP_STEPS.value: "1",
    GlueSettingKey.FORWARD_RAMP_STEPS.value: "3",

    RobotSettingKey.VELOCITY.value: "60",
    RobotSettingKey.ACCELERATION.value: "30",

}

class SegmentSettingsWidget(QWidget):
    save_requested = pyqtSignal()

    def __init__(self, keys: list[str], combo_enums: list[list], parent=None,segment=None,global_settings=False,pointManagerWidget=None):
        super().__init__(parent)
        self.parent=parent
        self.segment = segment
        if self.segment is not None:
            self.segmentSettings = self.segment.settings
        else:
            self.segmentSettings = None
        self.global_settings = global_settings
        self.pointManagerWidget = pointManagerWidget
        # self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.keys = keys
        self.combo_enums = {label: enum for label, enum in combo_enums}  # Convert to dict
        self.inputs = {}  # Dict[str, QWidget]
        self.init_ui()
        self.populate_values()


    def init_ui(self):
        layout = QVBoxLayout(self)

        for key in self.keys:
            row_layout = QHBoxLayout()

            label = QLabel(key)
            label.setMinimumWidth(150)
            row_layout.addWidget(label)

            if key in self.combo_enums:
                combo_box = QComboBox()
                combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

                enum_class = self.combo_enums[key]
                for enum_member in enum_class:
                    combo_box.addItem(enum_member.value)

                # Connect value change signal
                combo_box.currentTextChanged.connect(lambda val, k=key: self.on_value_changed(k, val))

                row_layout.addWidget(combo_box)
                self.inputs[key] = combo_box
            else:
                input_field = QDoubleSpinBox(parent=self.parent)
                input_field.setDecimals(3)
                input_field.setRange(-1e6, 1e6)
                input_field.setSingleStep(0.1)
                input_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                input_field.valueChanged.connect(lambda val, k=key: self.on_value_changed(k, str(val)))
                
                # Debug: Add additional focus event monitoring
                def debug_focus_in(event):

                    # Call the original focus event
                    QDoubleSpinBox.focusInEvent(input_field, event,)
                
                input_field.focusInEvent = debug_focus_in
                
                row_layout.addWidget(input_field)
                self.inputs[key] = input_field

            layout.addLayout(row_layout)

        # Add "Get Values" button
        get_button = QPushButton("Save")
        get_button.clicked.connect(self.print_values)
        layout.addWidget(get_button)

        layout.addStretch()

        self.setLayout(layout)

    def populate_values(self):
        # For global settings, always use the current default_settings
        if self.global_settings:
            settings_source = default_settings
        else:
            settings_source = self.segmentSettings if self.segmentSettings and self.segmentSettings != {} else default_settings

        for key, widget in self.inputs.items():
            value = settings_source.get(key, default_settings.get(key, ""))
            if isinstance(widget, QDoubleSpinBox):
                try:
                    widget.setValue(float(str(value).replace(",", "")) if str(value).strip() != "" else 0.0)
                except ValueError:
                    widget.setValue(0.0)
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value))
                if index >= 0:
                    widget.setCurrentIndex(index)
    
    def refresh_global_values(self):
        """Refresh the widget with current default settings (useful for global settings dialog)"""
        if self.global_settings:
            self.populate_values()
    
    def on_value_changed(self, key: str, value: str):
        print(f"[Value Changed] {key}: {value}")
        # if self.global_settings:
        #     self.pointManagerWidget.update_all_segments_settings()


    def print_values(self):
        values = self.get_values()
        print("[All Values]", values)
        self.save_requested.emit()

    def get_values(self) -> dict:
        """Return a dictionary with key: input text or selected combo."""
        result = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QDoubleSpinBox):
                result[key] = widget.value()
            elif isinstance(widget, QComboBox):
                result[key] = widget.currentText()

        if self.segment:
            self.segment.set_settings(result)
            print("segment settings", self.segment.settings)

        return result
    
    def get_global_values(self) -> dict:
        """Return a dictionary with key: input text or selected combo for global settings."""
        result = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QDoubleSpinBox):
                result[key] = widget.value()
            elif isinstance(widget, QComboBox):
                result[key] = widget.currentText()
        return result

    def set_values(self, values: dict):
        """Set values from a dict of key: value."""
        for key, val in values.items():
            widget = self.inputs.get(key)
            if isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(str(val).replace(",", "")))
            elif isinstance(widget, QComboBox):
                index = widget.findText(val)
                if index >= 0:
                    widget.setCurrentIndex(index)

    def clear(self):
        """Clear all input fields."""
        for widget in self.inputs.values():
            if isinstance(widget, QDoubleSpinBox):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)

# Settings file path
SETTINGS_FILE_PATH = os.path.join(os.path.dirname(__file__), "global_segment_settings.json")

def save_settings_to_file(settings: dict):
    """Save settings to a JSON file"""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(SETTINGS_FILE_PATH), exist_ok=True)
        
        with open(SETTINGS_FILE_PATH, 'w') as f:
            json.dump(settings, f, indent=2)
        print(f"Settings saved to {SETTINGS_FILE_PATH}")
    except Exception as e:
        print(f"Error saving settings to file: {e}")

def load_settings_from_file() -> dict:
    """Load settings from JSON file, return empty dict if file doesn't exist"""
    try:
        if os.path.exists(SETTINGS_FILE_PATH):
            with open(SETTINGS_FILE_PATH, 'r') as f:
                loaded_settings = json.load(f)
            print(f"Settings loaded from {SETTINGS_FILE_PATH}")
            return loaded_settings
        else:
            print(f"Settings file not found at {SETTINGS_FILE_PATH}, using defaults")
            return {}
    except Exception as e:
        print(f"Error loading settings from file: {e}")
        return {}

def initialize_default_settings():
    """Initialize default settings by loading from file if available"""
    global default_settings
    
    # Load settings from file
    file_settings = load_settings_from_file()
    
    # Update default_settings with loaded values, keeping original defaults as fallback
    if file_settings:
        for key, value in file_settings.items():
            if key in default_settings:  # Only update existing keys
                default_settings[key] = str(value)
        print("Default settings initialized with saved values")

def update_default_settings(new_settings: dict):
    """Update the global default settings dictionary and save to file"""
    global default_settings
    for key, value in new_settings.items():
        default_settings[key] = str(value)
    
    # Save to file
    save_settings_to_file(default_settings)
    print(f"Updated and saved default settings: {default_settings}")

def get_default_settings() -> dict:
    """Get the current default settings"""
    return default_settings.copy()

# Initialize default settings on module import
initialize_default_settings()

if __name__ == "__main__":
    from API.shared.settings.conreateSettings.enums.GlueSettingKey import GlueSettingKey
    from API.shared.settings.conreateSettings.enums.RobotSettingKey import RobotSettingKey
    from pl_ui.utils.enums.GlueType import GlueType

    from PyQt6.QtWidgets import QApplication
    import sys

    inputKeys = [key.value for key in GlueSettingKey]
    inputKeys.remove(GlueSettingKey.GLUE_TYPE.value)

    inputKeys.append(RobotSettingKey.VELOCITY.value)
    inputKeys.append(RobotSettingKey.ACCELERATION.value)

    comboEnums = [[GlueSettingKey.GLUE_TYPE.value, GlueType]]

    app = QApplication(sys.argv)
    widget = SegmentSettingsWidget(inputKeys + [GlueSettingKey.GLUE_TYPE.value], comboEnums)
    widget.show()
    sys.exit(app.exec())
