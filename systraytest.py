from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image

# --- State Management for Radio Buttons ---

# 1. A variable to hold the current state. We'll start with 'Mode 1' selected.
current_mode = 'Mode 1'

# 2. An action function. When a radio item is clicked, this function
#    will be called to update our state variable.
def set_mode(selected_mode):
    def action(icon, item):
        global current_mode
        current_mode = selected_mode
        print(f"Application mode changed to: {selected_mode}")
    return action

# 3. A function to check the state. This is used by the 'checked'
#    property of the menu item to determine if it should have a checkmark.
def is_checked(mode_name):
    def check(item):
        return current_mode == mode_name
    return check

# --- General Click Handler ---
def on_exit_clicked(icon, item):
    """A simple handler for the Exit button."""
    print("Exiting application...")
    icon.stop()

# --- Icon and Menu Setup ---

# Create a simple image for the icon
image = Image.new('RGB', (64, 64), color='blue')

# Create the dynamic menu.
# We put this inside a function that we can call.
# The radio buttons are grouped under a "Modes" submenu.
def create_menu():
    return menu(
        item(
            'Modes',
            menu(
                item(
                    'Mode 1',
                    set_mode('Mode 1'),
                    checked=is_checked('Mode 1'),
                    radio=True),
                item(
                    'Mode 2',
                    set_mode('Mode 2'),
                    checked=is_checked('Mode 2'),
                    radio=True),
                item(
                    'Mode 3',
                    set_mode('Mode 3'),
                    checked=is_checked('Mode 3'),
                    radio=True)
            )
        ),
        # A separator line for visual clarity
        menu.SEPARATOR,
        item(
            'Exit',
            on_exit_clicked
        )
    )

# Create and run the icon.
# Notice that we call create_menu() to build the menu structure.
app_icon = icon(
    'test_icon',
    image,
    'My System Tray App',
    menu=create_menu()
)

app_icon.run()