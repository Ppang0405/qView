#!/usr/bin/env python3

import sys

from PyQt6.QtWidgets import QApplication, QLabel


def main():
    app = QApplication(sys.argv)
    label = QLabel("Hello, qView!")
    label.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
