# Sorter User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [Using Sorter](#using-sorter)
6. [Customization](#customization)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## 1. Introduction

Sorter is a lightweight, efficient file organization tool designed for Ubuntu GNOME desktop environments. It provides a simple drag-and-drop interface to quickly sort files into predefined categories.

## 2. System Requirements

- Ubuntu 24 GNOME or compatible Linux distribution
- Python 3.6 or higher
- GTK 3.0
- Required Python packages: gi, requests

## 3. Installation

1. Ensure you have Python 3.6 or higher installed:
   ```
   python3 --version
   ```

2. Install required packages:
   ```
   sudo apt-get update
   sudo apt-get install python3-gi python3-requests
   ```

3. Download the `sorter.py` script to your preferred location.

## 4. Getting Started

1. Open a terminal and navigate to the directory containing `sorter.py`.
2. Run the script:
   ```
   python3 sorter.py
   ```
3. A brief notification will appear above your mouse cursor, confirming that Sorter is active.
4. The Sorter widget will be accessible on the right edge of your screen.

## 5. Using Sorter

### Accessing the Widget
- Move your mouse to the right edge of the screen to reveal the Sorter widget.
- The widget will automatically hide when you move your mouse away.

### Sorting Files
1. Drag a file from your desktop, file manager, or web browser.
2. Hover over the Sorter widget to reveal the drop zones.
3. Drop the file onto the appropriate category (Photos, Videos, Documents, Downloads).
4. The file will be moved to the corresponding folder in your home directory.

- Files with conflicting names will be automatically renamed with a numeric suffix to avoid overwriting.

### Opening Sorted Folders
- Click on any category button to open the corresponding folder in your file manager.

### Closing the Application
- Right-click on the widget and select "Close" from the context menu.

## 6. Customization

### Modifying Drop Zones
To change the default drop zones, edit the `zones` variable in the `sorter.py` script:

```python
zones = [
    ("Photos", "Pictures"),
    ("Videos", "Videos"),
    ("Documents", "Documents"),
    ("Downloads", "Downloads")
]
```

### Changing Widget Appearance
Modify the CSS in the `sorter.py` script to change the widget's appearance:

```python
css = b"""
.drop-success { background-color: #YourColor; }
.drop-error { background-color: #YourColor; }
"""
```

## 7. Troubleshooting

### Widget Not Appearing
- Ensure the script is running (check your terminal).
- Move your mouse to the far right edge of the screen.

### Drag and Drop Not Working
- Verify that you have the necessary permissions for the source and destination folders.
- Check the terminal for any error messages.

### Application Crashes
- Check the terminal for error messages.
- Ensure all required packages are installed and up to date.

### Widget Position Incorrect
- If the widget appears in the wrong position, ensure your display scaling settings are correct.
- The application now accounts for display scaling factors when positioning the widget.

## 8. FAQ

Q: Can I use Sorter on non-GNOME environments?
A: While designed for GNOME, Sorter may work on other environments with GTK support. However, full functionality is not guaranteed.

Q: How do I start Sorter automatically on system startup?
A: Add the command to run Sorter to your startup applications in your desktop environment settings.

Q: Is it possible to add more than four categories?
A: Yes, you can add more categories by modifying the `zones` variable in the script. Remember to adjust the widget size accordingly.

Q: Can I run multiple instances of Sorter?
A: No, Sorter is designed to run as a single instance. If you try to start a second instance, you'll see a notification informing you that Sorter is already running.

Q: Why do I see a notification when I start Sorter?
A: The notification is a quick confirmation that Sorter has started successfully. It appears briefly above your mouse cursor and then disappears.

Q: How does Sorter handle files with the same name?
A: Sorter automatically renames files with conflicting names by adding a numeric suffix, ensuring no files are overwritten.

Q: Does Sorter work correctly with high DPI displays?
A: Yes, Sorter now accounts for display scaling factors when positioning the widget and notifications.
