import pystray,threading, time
from PIL import Image, ImageDraw
from TailscaleCommands import setExitNode,GetTailwindStatus,Use_json,stateCallback,toggleTailscaleOnOff,executeTailscaleSetToggle 






class systemtray:
    """A class to manage the Tailscale system tray icon and its logic."""
    def __init__(self):
        # Initialize state by fetching it from your helper functions
        self.is_connected = stateCallback("onOff")
        self.all_exit_nodes = list(Use_json()["ExitNodes"].keys())
        self.selected_exit_node = Use_json()["UsedExitNode"]
        
        # An event to signal the main thread when the app should shut down
        self.shutdown_event = threading.Event()

        # Create the pystray.Icon object
        image = self._create_image()
        self.icon = pystray.Icon(
            "tray_icon",
            image,
            "Tailscale Tray",
            menu=self._create_menu()
        )

    def run(self):
        """Runs the icon in the current thread. This is a blocking call."""
        self.icon.run() # Fixed: Added parentheses to call the method

    def run_in_thread(self):
        """Runs the icon in a separate thread so the main program doesn't block."""
        # Fixed: Pass the method itself, not the result of calling it
        tray_thread = threading.Thread(target=self.icon.run)
        tray_thread.daemon = True
        tray_thread.start()

    def _toggle_connect(self, icon, item):
        """Handles the 'Connect' menu item click."""
        toggleTailscaleOnOff()
        # Improved: Re-check the state to ensure UI is accurate
        self.is_connected = stateCallback("onOff")
        print(f"Connect toggled. New status: {self.is_connected}")
        icon.update_menu()

    def _select_exit_node(self, icon, item):
        """Handles selecting an exit node from the submenu."""
        self.selected_exit_node = item.text
        
        if self.selected_exit_node == 'None':
            setExitNode("off")
        else:
            setExitNode(self.selected_exit_node)
        
        Use_json({"UsedExitNode": self.selected_exit_node}) # Persist the choice
        print(f"Selected exit node: {self.selected_exit_node}")
        icon.update_menu()

    def _on_quit(self, icon, item):
        """Handles the 'Quit' menu item click."""
        print("Quit clicked, stopping icon...")
        self.shutdown_event.set() # Signal main thread to exit
        self.icon.stop()

    def _create_exit_node_submenu(self):
        """Builds the dynamic exit node submenu."""
        ordered_nodes = [self.selected_exit_node]
        for node in self.all_exit_nodes:
            if node != self.selected_exit_node:
                ordered_nodes.append(node)

        menu_items = []
        for node_name in ordered_nodes:
            item = pystray.MenuItem(
                node_name,
                self._select_exit_node,
                checked=lambda item, name=node_name: self.selected_exit_node == name,
                radio=True
            )
            menu_items.append(item)
        return menu_items
    def update(self, icon):
        icon.update_menu()
        
        
    def _create_menu(self):
        """Builds the entire dynamic menu."""
        if GetTailwindStatus():
            
            status_line = GetTailwindStatus()
        else:
            status_line = "not connected"
        ip_address = status_line.split()[0].strip()
        device_name = status_line.split()[1].strip()

        exit_node_items = self._create_exit_node_submenu()
        return pystray.Menu(
            pystray.MenuItem(f"My IP: {ip_address}", None, enabled=False),
            pystray.MenuItem(f"Device Name: {device_name}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Connect', self._toggle_connect, checked=lambda item: self.is_connected, radio=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Exit nodes', pystray.Menu(*exit_node_items),enabled=stateCallback("onOff")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Refresh', self.update,),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('Quit', self._on_quit,)
        )

    def _create_image(self):
        try:
            image = Image.open("logo.png")
        except FileNotFoundError:
            # Fallback: Create a simple image
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "TS", fill='white')
        return image
    
    
#test =systemtray()
#print(test.icon)
#test.run()

