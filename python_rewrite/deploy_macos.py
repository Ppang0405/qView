#!/usr/bin/env python3
"""
qView Python Rewrite - macOS App Bundle Creator
Creates a proper macOS .app bundle for deployment
"""

import os
import shutil
import subprocess
import sys


def create_app_bundle():
    """Create macOS app bundle structure"""
    print("Creating macOS app bundle...")

    # App bundle structure
    bundle_name = "qView.app"
    contents_dir = f"{bundle_name}/Contents"
    macos_dir = f"{contents_dir}/MacOS"
    resources_dir = f"{contents_dir}/Resources"

    # Create directories
    os.makedirs(macos_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)

    # Create Info.plist
    info_plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>qView</string>
    <key>CFBundleDisplayName</key>
    <string>qView</string>
    <key>CFBundleIdentifier</key>
    <string>com.qview.python</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>qView</string>
    <key>CFBundleIconFile</key>
    <string>qView.icns</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Image files</string>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>jpg</string>
                <string>jpeg</string>
                <string>png</string>
                <string>gif</string>
                <string>bmp</string>
                <string>svg</string>
                <string>webp</string>
                <string>tiff</string>
                <string>tif</string>
            </array>
            <key>CFBundleTypeMIMETypes</key>
            <array>
                <string>image/jpeg</string>
                <string>image/png</string>
                <string>image/gif</string>
                <string>image/bmp</string>
                <string>image/svg+xml</string>
                <string>image/webp</string>
                <string>image/tiff</string>
            </array>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
        </dict>
    </array>
    <key>UTExportedTypeDeclarations</key>
    <array>
        <dict>
            <key>UTTypeIdentifier</key>
            <string>com.qview.image</string>
            <key>UTTypeDescription</key>
            <string>qView Image</string>
            <key>UTTypeConformsTo</key>
            <array>
                <string>public.image</string>
            </array>
            <key>UTTypeTagSpecification</key>
            <dict>
                <key>public.filename-extension</key>
                <array>
                    <string>jpg</string>
                    <string>jpeg</string>
                    <string>png</string>
                    <string>gif</string>
                    <string>bmp</string>
                    <string>svg</string>
                    <string>webp</string>
                    <string>tiff</string>
                    <string>tif</string>
                </array>
            </dict>
        </dict>
    </array>
</dict>
</plist>"""

    with open(f"{contents_dir}/Info.plist", "w") as f:
        f.write(info_plist)

    print(f"Created {contents_dir}/Info.plist")

    # Create launcher script
    launcher_script = """#!/bin/bash
# qView macOS launcher script

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set PYTHONPATH to include the Resources directory
export PYTHONPATH="$DIR/../Resources:$PYTHONPATH"

# Launch the Python application
exec python3 "$DIR/../Resources/main.py" "$@"
"""

    with open(f"{macos_dir}/qView", "w") as f:
        f.write(launcher_script)

    # Make launcher executable
    os.chmod(f"{macos_dir}/qView", 0o755)

    print(f"Created {macos_dir}/qView launcher script")

    # Copy Python files to Resources
    python_files = [
        "main.py",
        "qvapplication.py",
        "mainwindow.py",
        "qvgraphicsview.py",
        "qvimagecore.py",
        "actionmanager.py",
        "settingsmanager.py",
        "test_components.py",
    ]

    for file in python_files:
        if os.path.exists(file):
            shutil.copy2(file, resources_dir)
            print(f"Copied {file} to {resources_dir}")

    # Copy README and other resources
    if os.path.exists("README.md"):
        shutil.copy2("README.md", resources_dir)

    print(f"macOS app bundle created at {bundle_name}")
    return bundle_name


def create_dmg():
    """Create a DMG file for distribution"""
    print("Creating DMG for distribution...")

    bundle_name = "qView.app"
    dmg_name = "qView-1.0.0.dmg"

    if not os.path.exists(bundle_name):
        print(f"Error: {bundle_name} not found. Run create_app_bundle() first.")
        return

    # Create temporary directory for DMG contents
    temp_dir = "dmg_temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Copy app bundle to temp directory
    shutil.copytree(bundle_name, f"{temp_dir}/{bundle_name}")

    # Create Applications symlink
    os.symlink("/Applications", f"{temp_dir}/Applications")

    # Create DMG
    cmd = [
        "hdiutil",
        "create",
        "-volname",
        "qView",
        "-srcfolder",
        temp_dir,
        "-ov",
        "-format",
        "UDZO",
        dmg_name,
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"DMG created: {dmg_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating DMG: {e}")
    finally:
        # Clean up temp directory
        shutil.rmtree(temp_dir)


def main():
    """Main function"""
    print("qView macOS Deployment Tool")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "bundle":
            create_app_bundle()
        elif command == "dmg":
            create_dmg()
        elif command == "all":
            bundle = create_app_bundle()
            if bundle:
                create_dmg()
        else:
            print("Usage: python deploy_macos.py [bundle|dmg|all]")
    else:
        print("Creating app bundle...")
        create_app_bundle()


if __name__ == "__main__":
    main()
