#!/usr/bin/env python3

import sys

from PyQt6.QtCore import QCommandLineParser, QCoreApplication
from qvapplication import QVApplication


def main():
    print("Starting qView...")
    # Enable high DPI scaling
    # QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # TODO: Fix attribute

    # Set application info
    QCoreApplication.setOrganizationName("qView")
    QCoreApplication.setApplicationName("qView")
    QCoreApplication.setApplicationVersion("7.1")  # TODO: Use version from somewhere

    app = QVApplication(sys.argv)
    print("App created")

    parser = QCommandLineParser()
    parser.addHelpOption()
    parser.addVersionOption()
    parser.addPositionalArgument("file", "The file to open.")

    parser.process(app)

    # Create new window
    window = QVApplication.newWindow()
    print("Window created")

    # Open file if provided
    args = parser.positionalArguments()
    if args:
        QVApplication.openFile(window, args[0], True)
        print(f"Opening file: {args[0]}")

    print("Starting event loop...")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
