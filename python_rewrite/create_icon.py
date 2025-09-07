#!/usr/bin/env python3
"""
Create a simple icon for qView macOS app
"""

import os

from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication


def create_icon():
    """Create a simple qView icon"""
    app = QApplication([])  # QApplication needed for Qt functionality
    _ = app  # Suppress unused variable warning

    # Create a 512x512 pixmap
    pixmap = QPixmap(512, 512)
    pixmap.fill(QColor(70, 130, 180))  # Steel blue background

    # Create painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw a simple image icon (camera-like shape)
    painter.setPen(QColor(255, 255, 255))
    painter.setBrush(QColor(255, 255, 255))

    # Draw camera body
    painter.drawRoundedRect(100, 150, 312, 212, 20, 20)

    # Draw lens
    painter.setBrush(QColor(50, 50, 50))
    painter.drawEllipse(200, 200, 112, 112)

    # Draw inner lens
    painter.setBrush(QColor(30, 30, 30))
    painter.drawEllipse(230, 230, 52, 52)

    # Draw flash
    painter.setBrush(QColor(255, 255, 0))
    painter.drawRect(350, 180, 30, 20)

    # Draw text
    font = QFont("Arial", 48, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255))
    painter.drawText(200, 420, "qView")

    painter.end()

    # Save as PNG
    pixmap.save("qView.png")
    print("Created qView.png icon")

    # Create ICNS file (requires macOS)
    if os.uname().sysname == "Darwin":
        try:
            os.system("sips -s format icns qView.png --out qView.icns")
            print("Created qView.icns icon")
        except Exception as e:
            print(f"Could not create ICNS file: {e}")


if __name__ == "__main__":
    create_icon()

if __name__ == "__main__":
    create_icon()
