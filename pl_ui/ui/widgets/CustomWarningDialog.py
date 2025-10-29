from typing import Optional, Union

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QFrame, QWidget
)
from pl_ui.ui.widgets.MaterialButton import MaterialButton
from pl_ui.utils.styles.globalStyles import FONT

class CustomWarningDialog(QDialog):
    """Clean, flat, professional warning dialog"""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "Warning",
        message: str = "",
        info_text: str = ""
    ) -> None:
        super().__init__(parent)
        self.result_value: Optional[str] = None
        self.setup_dialog(title, message, info_text)

    def setup_dialog(self, title: str, message: str, info_text: str) -> None:
        """Setup the custom dialog styling and layout"""
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(420, 300)

        # Remove window frame for custom styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create clean container with rounded corners
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)

        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(24, 20, 24, 20)
        container_layout.setSpacing(16)

        # Header with warning icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Warning icon
        icon_label = QLabel("⚠")
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #dc2626;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 20px;
                padding: 8px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_font = QFont(FONT, 17)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                background: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        container_layout.addLayout(header_layout)

        # Main message
        message_label = QLabel(message)
        message_font = QFont(FONT, 13)
        message_label.setFont(message_font)
        message_label.setStyleSheet("""
            QLabel {
                color: #475569;
                background: transparent;
                border: none;
                line-height: 1.5;
                padding-left: 44px;
            }
        """)
        message_label.setWordWrap(True)
        container_layout.addWidget(message_label)

        # Info text (if provided)
        if info_text:
            info_label = QLabel(info_text)
            info_font = QFont(FONT, 12)
            info_label.setFont(info_font)
            info_label.setStyleSheet("""
                QLabel {
                    color: #64748b;
                    background: transparent;
                    border: none;
                    padding-left: 44px;
                    margin-top: 4px;
                }
            """)
            info_label.setWordWrap(True)
            container_layout.addWidget(info_label)

        container_layout.addStretch()

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border: none;
            }
        """)
        container_layout.addWidget(line)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 16, 0, 0)

        # Cancel button
        # self.cancel_button = QPushButton("Cancel")
        self.cancel_button = MaterialButton("Cancel")
        self.cancel_button.setFixedSize(100, 36)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_font = QFont(FONT, 18)
        cancel_font.setWeight(QFont.Weight.Medium)
        self.cancel_button.setFont(cancel_font)

        self.cancel_button.clicked.connect(self.reject_dialog)

        # OK button
        # self.ok_button = QPushButton("OK")
        self.ok_button = MaterialButton("OK")
        self.ok_button.setFixedSize(100, 36)
        self.ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_font = QFont(FONT, 12)
        ok_font.setWeight(QFont.Weight.Medium)
        self.ok_button.setFont(ok_font)

        self.ok_button.clicked.connect(self.accept_dialog)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        container_layout.addLayout(button_layout)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # Center the dialog on parent
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)

    def accept_dialog(self) -> None:
        """Handle OK button click"""
        self.result_value = "OK"
        self.accept()

    def reject_dialog(self) -> None:
        """Handle Cancel button click"""
        self.result_value = "Cancel"
        self.reject()

    def get_result(self) -> Optional[str]:
        """Get the result after dialog closes"""
        return self.result_value

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject_dialog()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.accept_dialog()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = CustomWarningDialog(
        title="Delete Item",
        message="Are you sure you want to delete this item?",
        info_text="This action cannot be undone."
    )
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print("User clicked OK")
    else:
        print("User clicked Cancel")
    sys.exit(app.exec())