import pystray
from PIL import Image, ImageDraw
from TailscaleCommands import GetTailwindStatus,Use_json,stateCallback

# --- 1. State Variables ---
is_connected = stateCallback("onOff")
all_exit_nodes = list(Use_json()["ExitNodes"].keys())
selected_exit_node = 'None'

# --- 2. Action and State Functions ---


def toggle_connect(icon, item):
    """Called when the 'Connect' menu item is clicked."""
    global is_connected
    is_connected = not is_connected
    print(f"Connect toggled. New status: {is_connected}")
    # We must call update_menu() to redraw the menu with the new state
    icon.update_menu()

def select_exit_node(icon, item):
    """Called when an exit node is selected. Updates state and rebuilds the menu."""
    global selected_exit_node
    selected_exit_node = item.text
    print(f"Selected exit node: {selected_exit_node}")
    # We must call update_menu() to rebuild the menu with the new order
    icon.update_menu()

def on_quit(icon, item):
    icon.stop()

# --- 3. Dynamic Menu Creation ---
# This part is the key fix. The entire menu is now built by a function.

def create_exit_node_submenu():
    """Builds the list of menu items for the exit node submenu."""
    ordered_nodes = [selected_exit_node]
    for node in all_exit_nodes:
        if node != selected_exit_node:
            ordered_nodes.append(node)

    menu_items = []
    for node_name in ordered_nodes:
        item = pystray.MenuItem(
            node_name,
            select_exit_node,
            # This lambda correctly checks the item's state when the menu is drawn
            checked=lambda item, name=node_name: selected_exit_node == name,
            radio=True
        )
        menu_items.append(item)
    
    return menu_items

def create_menu():
    """Dynamically creates the entire tray menu on demand."""
    # This function is called every time icon.update_menu() runs.
    
    # We call our function to get the list of MenuItem objects for the submenu
    exit_node_items = create_exit_node_submenu()

    # Build the full menu
    menu = pystray.Menu(
        pystray.MenuItem(
            lambda text: f"My IP: {(GetTailwindStatus().split()[0].strip())}",
            None,
            enabled=False),
        pystray.MenuItem(
            lambda text: f"Device Name: {(GetTailwindStatus().split()[1].strip())}",
            None,
            enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            'Connect',
            toggle_connect,
            checked=lambda item: is_connected,
            radio=True),
        pystray.Menu.SEPARATOR,
        # The submenu is now correctly created during the menu build process
        pystray.MenuItem(
            'Exit nodes',
            pystray.Menu(*exit_node_items)
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Quit', on_quit)
    )
    return menu


# --- 4. Placeholder Icon Image ---
def create_image():
    image = Image.new('RGB', (64, 64), 'black')
    dc = ImageDraw.Draw(image)
    dc.rectangle((10, 10, 54, 54), fill='white')
    return image


# --- 5. Main Setup ---
def setup_tray():
    icon_image = create_image()
    # Here is the fix: we pass the create_menu function to the icon,
    # not a static menu object.
    icon = pystray.Icon(
        "tray_icon",
        icon_image,
        "Board",
        menu=create_menu() # Pass the function that generates the menu
    )
    icon.run()


if __name__ == "__main__":
    setup_tray()