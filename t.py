import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        win = Gtk.ApplicationWindow(application=app)
        win.set_default_size(300, 350)
        win.set_title("Scrollable ListBox Example")

        # 1. Create the ListBox and populate it with many items
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        for i in range(1, 31):
            list_box.append(Gtk.Label(label=f"List Item #{i}"))

        # 2. Create a ScrolledWindow to hold the ListBox
        scrolled_window = Gtk.ScrolledWindow()
        
        # 3. Control the height of the scrollable area
        # The width is -1 (natural), the height is 200px
        scrolled_window.set_size_request(-1, 200)

        # 4. Set the ListBox as the child of the ScrolledWindow
        scrolled_window.set_child(list_box)

        # Add the ScrolledWindow (not the ListBox) to the main window
        win.set_child(scrolled_window)
        win.present()

if __name__ == "__main__":
    app = MyApp(application_id="com.example.ScrollableList")
    app.run(sys.argv)