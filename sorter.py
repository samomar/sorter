import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os
import urllib.parse
import shutil
import logging
import requests
from urllib.parse import urlparse
from datetime import datetime
import subprocess
import fcntl
import sys

# Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.CRITICAL)  # or logging.ERROR

def ensure_single_instance():
    lock_file = '/tmp/sorter.lock'
    try:
        fp = open(lock_file, 'w')
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fp  # Keep the file handle open to maintain the lock
    except IOError:
        return None  # Return None if lock couldn't be acquired

class DropZone(Gtk.Button):
    def __init__(self, label, target_folder):
        super().__init__(label=label)
        self.target_folder = target_folder
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("clicked", self.on_click)
        self.connect("button-press-event", self.on_button_press)
        self.drag_dest_add_uri_targets()
        self.drag_dest_add_text_targets()

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        logging.info(f"Drag received in {self.get_label()} zone - Type: {info}")
        
        try:
            if info == 0:  # URI
                uris = data.get_uris()
                if uris:
                    for uri in uris:
                        self.process_uri(uri)
                else:
                    text = data.get_text()
                    if text:
                        self.process_text(text)
                    else:
                        logging.warning("Received empty data")
            elif info == 1:  # Text
                text = data.get_text()
                if text:
                    self.process_text(text)
                else:
                    logging.warning("Received empty text data")
            else:
                logging.warning(f"Unsupported drop type: {info}")
            
            self.get_style_context().add_class('drop-success')
            GLib.timeout_add(1000, self.reset_style)
        except Exception as e:
            logging.error(f"Error processing drag data: {e}")
            self.get_style_context().add_class('drop-error')
            GLib.timeout_add(1000, self.reset_style)
        
        drag_context.finish(True, False, time)

    def reset_style(self):
        self.get_style_context().remove_class('drop-success')
        self.get_style_context().remove_class('drop-error')
        return False

    def process_uri(self, uri):
        file_path = self.uri_to_path(uri)
        if file_path:
            self.move_file(file_path)
        else:
            self.download_file(uri)

    def process_text(self, text):
        if text.startswith(('http://', 'https://')):
            self.download_file(text)
        elif os.path.exists(text):
            self.move_file(text)
        else:
            self.save_text_as_file(text)

    def uri_to_path(self, uri):
        file_path = urllib.parse.unquote(uri)
        if file_path.startswith('file://'):
            return file_path[7:]
        elif os.path.exists(file_path):
            return file_path
        return None

    def move_file(self, file_path):
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(self.target_folder, file_name)
        try:
            shutil.move(file_path, dest_path)
            logging.info(f"Moved {file_name} to {self.target_folder}")
        except Exception as e:
            logging.error(f"Error moving file: {e}")

    def save_text_as_file(self, text):
        file_name = f"dropped_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        dest_path = os.path.join(self.target_folder, file_name)
        try:
            with open(dest_path, 'w') as f:
                f.write(text)
            logging.info(f"Saved text as {file_name} in {self.target_folder}")
        except Exception as e:
            logging.error(f"Error saving text as file: {e}")

    def download_file(self, url):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # Parse the URL to get the original file name
                parsed_url = urlparse(url)
                original_file_name = os.path.basename(parsed_url.path)
                
                # If no file name is found, use a default name
                if not original_file_name:
                    content_type = response.headers.get('content-type', '')
                    ext = content_type.split('/')[-1] if 'image' in content_type else 'file'
                    original_file_name = f"downloaded.{ext}"

                # Prepend the current date to the file name
                date_prefix = datetime.now().strftime('%Y%m%d_')
                file_name = f"{date_prefix}{original_file_name}"
                
                dest_path = os.path.join(self.target_folder, file_name)
                
                # Ensure the file name is unique
                counter = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(file_name)
                    file_name = f"{name}_{counter}{ext}"
                    dest_path = os.path.join(self.target_folder, file_name)
                    counter += 1

                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logging.info(f"Downloaded {file_name} to {self.target_folder}")
            else:
                logging.error(f"Failed to download {url}. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error downloading file: {e}")

    def on_click(self, widget):
        try:
            subprocess.run(['xdg-open', self.target_folder])
            logging.info(f"Opened folder: {self.target_folder}")
        except Exception as e:
            logging.error(f"Error opening folder: {e}")

    def on_button_press(self, widget, event):
        if event.button == 3:  # Right mouse button
            self.get_toplevel().show_context_menu(event)
            return True
        return False

class DockWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.POPUP)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.box)

        home_dir = os.path.expanduser("~")
        zones = [
            ("Photos", "Pictures"),
            ("Videos", "Videos"),
            ("Documents", "Documents"),
            ("Downloads", "Downloads")
        ]

        for label, folder in zones:
            target_folder = os.path.join(home_dir, folder)
            os.makedirs(target_folder, exist_ok=True)
            zone = DropZone(label, target_folder)
            self.box.pack_start(zone, True, True, 0)

        self.set_size_request(100, 300)
        self.move_to_right_edge()

        self.mouse_inside = False
        self.connect("enter-notify-event", self.on_enter)
        self.connect("leave-notify-event", self.on_leave)
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)

        self.connect("button-press-event", self.on_button_press)

        # Add this line to show a quick startup notification
        GLib.timeout_add(100, self.show_startup_notification)

    def move_to_right_edge(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()
        self.move(geometry.width - 100, (geometry.height - 300) // 2)

    def on_enter(self, widget, event):
        self.mouse_inside = True

    def on_leave(self, widget, event):
        self.mouse_inside = False

    def on_button_press(self, widget, event):
        if event.button == 3:  # Right mouse button
            self.show_context_menu(event)
            return True
        return False

    def show_context_menu(self, event):
        menu = Gtk.Menu()
        close_item = Gtk.MenuItem(label="Close")
        close_item.connect("activate", self.on_close)
        menu.append(close_item)
        menu.show_all()
        menu.popup_at_pointer(event)

    def on_close(self, widget):
        Gtk.main_quit()

    def show_startup_notification(self):
        notification = Gtk.Window(type=Gtk.WindowType.POPUP)
        notification.set_decorated(False)
        
        label = Gtk.Label(label="Sorter is active")
        
        # Create a box to hold the label and set padding
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.pack_start(label, True, True, 0)
        
        notification.add(box)
        
        # Get current mouse position
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        device = seat.get_pointer()
        screen, x, y = device.get_position()
        
        # Set notification size
        notification.set_default_size(120, 40)
        
        # Position the notification above the mouse cursor
        notification.move(x - 60, y - 50)  # Adjust these values as needed
        
        notification.show_all()
        
        # Hide the notification after 1 second
        GLib.timeout_add(1000, notification.destroy)
        return False

def check_cursor_position(window):
    display = Gdk.Display.get_default()
    seat = display.get_default_seat()
    device = seat.get_pointer()
    screen, x, y = device.get_position()
    
    win_pos = window.get_position()
    win_size = window.get_size()
    
    if x >= win_pos[0] - 10 and x < win_pos[0] + win_size[0] and y >= win_pos[1] and y < win_pos[1] + win_size[1]:
        window.show_all()
    else:
        window.hide()
    
    return True

if __name__ == "__main__":
    lock = ensure_single_instance()
    
    if lock is None:
        # Another instance is running, show notification and exit
        notification = Gtk.Window(type=Gtk.WindowType.POPUP)
        notification.set_decorated(False)
        
        label = Gtk.Label(label="Another instance of Sorter is already running")
        label.set_padding(20, 10)
        notification.add(label)
        
        # Get current mouse position
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        device = seat.get_pointer()
        screen, x, y = device.get_position()
        
        # Set notification size and position
        notification.set_default_size(250, 40)
        notification.move(x - 125, y - 50)  # Center above mouse cursor
        
        notification.show_all()
        
        # Hide the notification and exit after 2 seconds
        GLib.timeout_add(2000, lambda: (notification.destroy(), sys.exit(1)))
        Gtk.main()
    else:
        # Normal startup
        css = b"""
        .drop-success {
            background-color: #4CAF50;
        }
        .drop-error {
            background-color: #F44336;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        win = DockWindow()
        win.connect("destroy", Gtk.main_quit)

        GLib.timeout_add(100, check_cursor_position, win)

        Gtk.main()
        
        # Release the lock when the application exits
        lock.close()
