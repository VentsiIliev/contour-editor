from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QLineEdit, QFormLayout, QFrame, QScrollArea
)
from dataclasses import dataclass, field
from typing import List, Optional

# ==========================================================
# FIELD CLASS
# ==========================================================
@dataclass
class Field:
    label: str
    key: str
    type: str  # "float", "int", "str", "combo"
    placeholder: Optional[str] = None
    options: Optional[List[str]] = field(default_factory=list)

# ==========================================================
# HELPER EMITTER CLASS FOR SIGNALS
# ==========================================================
class FieldSignalEmitter(QObject):
    valueChanged = pyqtSignal(object)  # emits the new value

# ==========================================================
# GENERIC FORM WIDGET
# ==========================================================
# ==========================================================
# GENERIC FORM WIDGET WITH ATTRIBUTE SIGNALS
# ==========================================================
class GenericFormWidget(QWidget):
    applyClicked = pyqtSignal(dict)
    cancelClicked = pyqtSignal()

    def __init__(self, fields: List[Field], title: str = "Form", parent=None):
        super().__init__(parent)
        self.fields = fields
        self.setMinimumWidth(500)
        self.setMinimumHeight(700)
        self.setWindowTitle(title)
        self.inputs = {}
        self.title = title
        self.signals = {}  # keep dictionary if needed
        self.init_ui()
        self.create_field_signals()

    def create_field_signals(self):
        for field_def in self.fields:
            key = field_def.key
            emitter = FieldSignalEmitter()
            self.signals[key] = emitter

            # Also create a dynamic attribute on self: e.g. self.velocityChanged
            setattr(self, f"{key}Changed", emitter.valueChanged)

            widget = self.inputs[key]
            if field_def.type == "combo":
                widget.currentTextChanged.connect(lambda val, k=key: self.emit_field_signal(k, val))
            else:
                widget.textChanged.connect(lambda val, k=key: self.emit_field_signal(k, val))


    # ======================================================
    # UI SETUP
    # ======================================================
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        form_layout = QFormLayout(content_widget)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        for field_def in self.fields:
            key = field_def.key
            if field_def.type == "combo":
                widget = QComboBox()
                widget.addItems(field_def.options)
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(field_def.placeholder or "")

            self.inputs[key] = widget
            form_layout.addRow(field_def.label + ":", widget)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        apply_button.clicked.connect(self.on_apply_clicked)

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        cancel_button.clicked.connect(self.on_cancel_clicked)

        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)


    def emit_field_signal(self, key, value):
        field_def = next((f for f in self.fields if f.key == key), None)
        if not field_def:
            return

        # Convert value
        if field_def.type == "float":
            try:
                value = float(value)
            except ValueError:
                value = 0.0
        elif field_def.type == "int":
            try:
                value = int(value)
            except ValueError:
                value = 0

        print(f"[{self.title}] Field '{key}' changed -> {value}")
        self.signals[key].valueChanged.emit(value)

    # ======================================================
    # EVENT HANDLERS
    # ======================================================
    def on_apply_clicked(self):
        data = {}
        for field_def in self.fields:
            key = field_def.key
            widget = self.inputs[key]

            if field_def.type == "combo":
                data[key] = widget.currentText()
            elif field_def.type == "float":
                try:
                    data[key] = float(widget.text().strip())
                except ValueError:
                    data[key] = 0.0
            elif field_def.type == "int":
                try:
                    data[key] = int(widget.text().strip())
                except ValueError:
                    data[key] = 0
            else:
                data[key] = widget.text().strip()

        print(f"[{self.title}] Apply clicked ->", data)
        self.applyClicked.emit(data)

    def on_cancel_clicked(self):
        print(f"[{self.title}] Cancel clicked")
        self.cancelClicked.emit()
        self.reset_fields()

    def reset_fields(self):
        for field_def in self.fields:
            widget = self.inputs[field_def.key]
            if field_def.type == "combo":
                widget.setCurrentIndex(0)
            else:
                widget.clear()

# ==========================================================
# STANDALONE DEMO
# ==========================================================
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    # DEFINE FIELDS
    demo_fields = [
        Field(label="Glue Type", key="glue_type", type="combo",
              options=["Hot Glue", "Cold Glue", "Epoxy", "Silicone", "UV Adhesive"]),
        Field(label="Glue Pressure", key="glue_pressure", type="float", placeholder="Enter glue pressure (bar)"),
        Field(label="Velocity", key="velocity", type="float", placeholder="Enter velocity (mm/s)"),
        Field(label="Operator Name", key="operator", type="str", placeholder="Enter your name"),
    ]

    app = QApplication([])

    # CREATE A FORM INSTANCE USING THE FIELDS DEFINED ABOVE
    form = GenericFormWidget(fields=demo_fields, title="Global Settings Form")
    form.show()

    # CONNECT SIGNALS TO PRINT CHANGES
    form.velocityChanged.connect(lambda val: print(f"Velocity changed -> {val}"))
    form.operatorChanged.connect(lambda val: print(f"Operator changed -> {val}"))

    # CONNECT APPLY AND CANCEL SIGNALS
    form.applyClicked.connect(lambda data: print("Applied:", data))
    form.cancelClicked.connect(lambda: print("Cancelled"))

    app.exec()
