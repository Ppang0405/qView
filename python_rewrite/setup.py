"""
qView - A minimal image viewer
Python rewrite of the popular qView image viewer
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qview",
    version="1.0.0",
    author="qView Python Rewrite",
    author_email="",
    description="A minimal image viewer - Python rewrite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ppang0405/qView",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Graphics :: Viewers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "qview=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
