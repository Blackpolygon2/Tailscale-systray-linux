import os
import sys
from PIL import Image, ImageDraw
import threading
import time
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QActionGroup
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt5.QtCore import QUrl
from TailscaleCommands import setExitNode, GetTailwindStatus, Use_json, stateCallback, toggleTailscaleOnOff
import logging

logging.basicConfig(
    filename='systray.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
class SystemTray:

    def __init__(self, app):
        self.app = app

        self.is_connected = stateCallback("onOff")
        self.all_exit_nodes = list(Use_json()["ExitNodes"].keys())
        self.selected_exit_node = Use_json()["UsedExitNode"]
        self.shutdown_event = threading.Event()

        logging.debug("systray made")
        self.tray_icon = QSystemTrayIcon(self._create_image(), self.app)
        self.tray_icon.setToolTip("Tailscale Tray")
        self.tray_icon.activated.connect(self._on_activated)
        self._create_menu()
        self.tray_icon.show()
        logging.debug("systray shown")

    def run(self):
        self.app.exec_()

    def _toggle_connect(self):
        toggleTailscaleOnOff()
        self.is_connected = stateCallback("onOff")
        print(f"Connect toggled. New status: {self.is_connected}")
        self._create_menu()

    def _select_exit_node(self, node_name):
        self.selected_exit_node = node_name
        if self.selected_exit_node == 'None':
            setExitNode("off")
        else:
            setExitNode(self.selected_exit_node)
        Use_json({"UsedExitNode": self.selected_exit_node})
        print(f"Selected exit node: {self.selected_exit_node}")
        self._create_menu()

    def _on_quit(self):
        print("Quit clicked, stopping icon...")
        self.shutdown_event.set()
        self.tray_icon.hide()
        self.app.quit()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_website

    def _create_exit_node_submenu(self, menu):
        ordered_nodes = [self.selected_exit_node]
        for node in self.all_exit_nodes:
            if node != self.selected_exit_node:
                ordered_nodes.append(node)

        exit_node_menu = QMenu("Exit nodes", menu)
        group = QActionGroup(menu)
        group.setExclusive(True)

        for node_name in ordered_nodes:
            action = exit_node_menu.addAction(node_name)
            action.setCheckable(True)
            action.setChecked(self.selected_exit_node == node_name)
            action.triggered.connect(
                lambda checked, name=node_name: self._select_exit_node(name))
            group.addAction(action)

        return exit_node_menu

    def _create_menu(self):
        menu = QMenu()

        if GetTailwindStatus():
            status_line = GetTailwindStatus()
        else:
            status_line = "not connected"
        ip_address = status_line.split()[0].strip()
        device_name = status_line.split()[1].strip()

        # IP Address (disabled)
        ip_action = menu.addAction(f"My IP: {ip_address}")
        ip_action.setEnabled(False)

        # Device Name (disabled)
        device_action = menu.addAction(f"Device Name: {device_name}")
        device_action.setEnabled(False)

        menu.addSeparator()

        # Connect toggle
        connect_action = menu.addAction("Connect")
        connect_action.setCheckable(True)
        connect_action.setChecked(self.is_connected)
        connect_action.triggered.connect(self._toggle_connect)

        menu.addSeparator()

        # Exit nodes submenu
        exit_node_menu = self._create_exit_node_submenu(menu)
        exit_node_menu.setEnabled(stateCallback("onOff"))
        menu.addMenu(exit_node_menu)

        menu.addSeparator()

        # Refresh
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self._create_menu)

        menu.addSeparator()

        # Quit
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._on_quit)

        self.tray_icon.setContextMenu(menu)

    def _create_image(self):

        try:
            image = Image.open("logo.png")
        except FileNotFoundError:
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "TS", fill='white')

        image.save("temp_icon.png")
        pixmap = QPixmap("temp_icon.png")
        os.remove("temp_icon.png")
        return QIcon(pixmap)

    
