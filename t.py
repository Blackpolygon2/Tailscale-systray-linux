import os
import sys
import threading
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QAction
from PyQt5.QtGui import QIcon, QPixmap
from TailscaleCommands import setExitNode, GetTailwindStatus, Use_json, stateCallback, toggleTailscaleOnOff, executeTailscaleSetToggle


class SystemTray:
    """A class to manage the Tailscale system tray icon and its logic using PyQt5."""

    def __init__(self, app):
        self.app = app  # QApplication instance
        self.is_connected = stateCallback("onOff")
        self.all_exit_nodes = list(Use_json()["ExitNodes"].keys())
        self.selected_exit_node = Use_json()["UsedExitNode"]
        self.shutdown_event = threading.Event()

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self._create_image(), self.app)
        self.tray_icon.setToolTip("Tailscale Tray")
        self.tray_icon.activated.connect(self._on_tray_activated)

       

        # Create and set initial menu
        self._update_menu()
        self.tray_icon.setContextMenu(self._create_menu())
        self.tray_icon.show()
        
        
        
        

    def _on_tray_activated(self, reason):
        """Handle tray icon activation (e.g., double-click to show GUI)."""
        """if reason == QSystemTrayIcon.DoubleClick:
            self.GTKUI.show_window()"""

    def _toggle_connect(self):
        """Handles the 'Connect' menu item click."""
        toggleTailscaleOnOff()
        self.is_connected = stateCallback("onOff")
        print(f"Connect toggled. New status: {self.is_connected}")
        self._update_menu()

    def _select_exit_node(self, node_name):
        """Handles selecting an exit node from the submenu."""
        self.selected_exit_node = node_name
        if self.selected_exit_node == 'None':
            setExitNode("off")
        else:
            setExitNode(self.selected_exit_node)
        Use_json({"UsedExitNode": self.selected_exit_node})
        print(f"Selected exit node: {self.selected_exit_node}")
        self._update_menu()

    def _on_quit(self):
        """Handles the 'Quit' menu item click."""
        print("Quit clicked, stopping icon...")
        self.shutdown_event.set()
        self.tray_icon.hide()
        self.app.quit()

    def _create_exit_node_submenu(self):
        """Builds the dynamic exit node submenu."""
        submenu = QMenu("Exit nodes")
        ordered_nodes = [self.selected_exit_node]
        for node in self.all_exit_nodes:
            if node != self.selected_exit_node:
                ordered_nodes.append(node)

        for node_name in ordered_nodes:
            action = QAction(node_name, submenu)
            action.setCheckable(True)
            action.setChecked(self.selected_exit_node == node_name)
            # Create a closure to capture node_name
            action.triggered.connect(lambda checked, name=node_name: self._select_exit_node(name))
            submenu.addAction(action)
        submenu.setEnabled(stateCallback("onOff"))
        return submenu

    def _update_menu(self):
        """Updates the tray menu."""
        self.tray_icon.setContextMenu(self._create_menu())

    def _create_menu(self):
        """Builds the entire dynamic menu."""
        menu = QMenu()

        # Get status information
        status_line = GetTailwindStatus() or "not connected"
        ip_address = status_line.split()[0].strip()
        device_name = status_line.split()[1].strip()

        # Show Message (default action)
        """show_action = QAction("Show Message", menu)
        show_action.triggered.connect(self.GTKUI.show_window)
        menu.addAction(show_action)"""

        # IP and Device Name (disabled)
        ip_action = QAction(f"My IP: {ip_address}", menu)
        ip_action.setEnabled(False)
        menu.addAction(ip_action)

        device_action = QAction(f"Device Name: {device_name}", menu)
        device_action.setEnabled(False)
        menu.addAction(device_action)

        # Separator
        menu.addSeparator()

        # Connect toggle
        connect_action = QAction("Connect", menu)
        connect_action.setCheckable(True)
        connect_action.setChecked(self.is_connected)
        connect_action.triggered.connect(self._toggle_connect)
        menu.addAction(connect_action)

        # Separator
        menu.addSeparator()

        # Exit nodes submenu
        menu.addMenu(self._create_exit_node_submenu())

        # Separator
        menu.addSeparator()

        # Refresh action
        refresh_action = QAction("Refresh", menu)
        refresh_action.triggered.connect(self._update_menu)
        menu.addAction(refresh_action)

        # Separator
        menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self._on_quit)
        menu.addAction(quit_action)
        print ('menu')
        return menu

    def _create_image(self):
        """Creates the tray icon image."""
        try:
            image = Image.open("logo.png")
        except FileNotFoundError:
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "TS", fill='white')
        
        # Convert PIL Image to QPixmap
        image.save("temp_icon.png")  # Save temporarily to load into QPixmap
        pixmap = QPixmap("temp_icon.png")
        os.remove("temp_icon.png")  # Clean up
        return QIcon(pixmap)

def main():
    app = QApplication(sys.argv)
    tray = SystemTray(app)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()