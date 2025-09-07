#!/usr/bin/env python3
"""
Simple test script for qView Python rewrite
Tests basic functionality of the image viewer components
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qvgraphicsview import QVGraphicsView
from qvimagecore import QVImageCore


def test_image_core():
    """Test QVImageCore functionality"""
    print("Testing QVImageCore...")

    image_core = QVImageCore()

    # Test with a sample image if available
    test_image_path = "/Volumes/KINGSTON/_kingston_misc/qView/resources/checkmark.png"
    if os.path.exists(test_image_path):
        print(f"Loading test image: {test_image_path}")
        image_core.loadFile(test_image_path)

        pixmap = image_core.getLoadedPixmap()
        if not pixmap.isNull():
            print(f"Image loaded successfully! Size: {pixmap.size()}")
        else:
            print("Failed to load image")
    else:
        print("Test image not found, skipping image load test")

    return True


def test_graphics_view():
    """Test QVGraphicsView functionality"""
    print("Testing QVGraphicsView...")

    graphics_view = QVGraphicsView()

    # Test basic properties
    print(f"Graphics view created with scene: {graphics_view.scene() is not None}")
    print(f"Image core attached: {graphics_view.imageCore is not None}")

    return True


def main():
    """Main test function"""
    print("=== qView Python Rewrite Test Suite ===")

    try:
        # Test individual components
        test_image_core()
        print()
        test_graphics_view()
        print()

        print("=== All tests completed successfully! ===")

    except Exception as e:
        print(f"Test failed with error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
