import os, requests
from PIL import Image, ImageDraw
import threading
from io import BytesIO
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from TailscaleCommands import send_notification, executeTailscaleSetToggle, setExitNode, GetTailwindStatus, get_and_set_state_json, stateCallback, toggleTailscaleOnOff
import logging
import webbrowser

path = os.path.expanduser("~/.TailscaleSystemTray")
logging.basicConfig(
    filename=os.path.join(path, 'systray.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class SystemTray:

    def __init__(self, app):
        self.app = app

        self.is_connected = stateCallback("onOff")
        self.is_exitnode = stateCallback("exitNode")
        self.is_ssh = stateCallback("ssh")
        self.is_acceptroutes = stateCallback("AcceptRoutes")
        self.all_exit_nodes = list(get_and_set_state_json()["ExitNodes"].keys())
        self.selected_exit_node = get_and_set_state_json()["UsedExitNode"]
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

    def _update_state(self):
        self.is_connected = stateCallback("onOff")
        self.is_exitnode = stateCallback("exitNode")
        self.is_ssh = stateCallback("ssh")
        self.is_acceptroutes = stateCallback("AcceptRoutes")
        self._create_menu()

    def _toggle_connect(self):
        executeTailscaleSetToggle("onOff")

        self._update_state
        send_notification(f"Tailscale connection toggled {self.is_connected}")

    def _toggle_ssh(self):
        executeTailscaleSetToggle("ssh")

        self._update_state
        send_notification(f"Tailscale SSH service toggled {self.is_ssh}")

    def _toggle_accept_routes(self):
        executeTailscaleSetToggle("acceptRoutes")

        self._update_state
        send_notification(
            f"Tailscale accept routes toggled {self.is_acceptroutes}")

    def _toggle_adv_as_exit_node(self):
        executeTailscaleSetToggle("exitNode")
        
        self._update_state
        send_notification(f"Tailscale advertising as exit node {self.is_exitnode}")

    def _select_exit_node(self, node_name):
        self.selected_exit_node = node_name
        if self.selected_exit_node == 'None':
            setExitNode("off")
        else:
            setExitNode(self.selected_exit_node)
        get_and_set_state_json({"UsedExitNode": self.selected_exit_node})
        logging.debug(f"Selected exit node: {self.selected_exit_node}")
        self._create_menu()

    def _on_quit(self):
        logging.debug("Quit clicked, stopping icon...")
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

        show_panel_action = menu.addAction("Show panel")
        show_panel_action.triggered.connect(
            lambda: webbrowser.open("http://100.100.100.100/"))

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

        ssh_action = menu.addAction("SSH")
        ssh_action.setCheckable(True)
        ssh_action.setChecked(self.is_ssh)
        ssh_action.triggered.connect(self._toggle_ssh)

        advertise_exit_node_action = menu.addAction("Advertise As Exit Node")
        advertise_exit_node_action.setCheckable(True)
        advertise_exit_node_action.setChecked(self.is_exitnode)
        advertise_exit_node_action.triggered.connect(
            self._toggle_adv_as_exit_node)

        accept_routes_action = menu.addAction("Accept Routes")
        accept_routes_action.setCheckable(True)
        accept_routes_action.setChecked(self.is_acceptroutes)
        accept_routes_action.triggered.connect(self._toggle_accept_routes)

        menu.addSeparator()

        # Quit
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._on_quit)

        self.tray_icon.setContextMenu(menu)

    def _create_image(self):

        try:
            image = Image.open("logo.png")
        except FileNotFoundError:
            try:
                response = requests.get("https://tailscale.gallerycdn.vsassets.io/extensions/tailscale/vscode-tailscale/1.0.0/1698786256133/Microsoft.VisualStudio.Services.Icons.Default")
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            except:
                image = Image.new('RGB', (64, 64), color='blue')
                draw = ImageDraw.Draw(image)
                draw.text((10, 10), "TS", fill='white')

        image.save("temp_icon.png")
        pixmap = QPixmap("temp_icon.png")
        os.remove("temp_icon.png")
        return QIcon(pixmap)
