#adwactionmrow
import TailscaleCommands as TS #cause this shit is so. lemme stop myself 
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Adw, WebKit,GdkPixbuf

class GtkGUI(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        self.connect('activate', self.on_activate)
    WebKit.WebView()
    
    
    def refresh_app(self):
        if self.webview:
            self.webview.load_uri("http://100.100.100.100/")    
        if TS.stateCallback("onOff"):
            self.ConnectionSwitch.set_subtitle("connected")
        else:
            self.ConnectionSwitch.set_subtitle("not connected")
        
        self.ConnectionSwitch.set_active(TS.stateCallback("onOff"))
        self.ConnectionSwitch.connect("notify::active", self.handle_switches)
        self.ConnectionSwitch.set_title(TS.GetTailwindStatus().split()[2])
        
        self.ExitNodesRow.set_subtitle(TS.Use_json()["UsedExitNode"])
        
        self.SSHswitch.set_active(TS.stateCallback("ssh"))
        self.SSHswitch.connect("notify::active", self.handle_switches)
        
        self.AdvertiseAsExitNodeSwitch.set_active(TS.stateCallback("exitNode"))
        self.AdvertiseAsExitNodeSwitch.connect("notify::active", self.handle_switches)
        
        self.AcceptRoutesSwitch.set_active(TS.stateCallback("AcceptRoutes"))
        self.AcceptRoutesSwitch.connect("notify::active", self.handle_switches)
        
    def refresh_switches(self):
        self.AcceptRoutesSwitch.set_active(TS.stateCallback("AcceptRoutes"))
        self.AdvertiseAsExitNodeSwitch.set_active(TS.stateCallback("exitNode"))
        self.SSHswitch.set_active(TS.stateCallback("ssh"))
        
        
    def handle_switches(self, widget, state):
           TS.executeTailscaleSetToggle(widget.get_name())
           self.webview.load_uri("http://100.100.100.100/")
           
            
    
    def on_activate(self, app):
        
        builder = Gtk.Builder()
        builder.add_from_file("UI/tailscalegui.ui")

        #declare objects
        self.webview = builder.get_object("TailscaleWebview")
        self.ConnectionSwitch = builder.get_object("onOffSwitch")
        self.SSHswitch = builder.get_object("SSHswitch")
        self.AdvertiseAsExitNodeSwitch = builder.get_object("AdvertiseAsExitNodeSwitch")
        self.AcceptRoutesSwitch = builder.get_object("AcceptRoutesSwitch")
        self.ExitNodesRow = builder.get_object("ExitNodesRow")
        self.ExitNodesList = builder.get_object("ExitNodesList")
        self.ShareFilesButton = builder.get_object("ShareFilesButton")
        self.ReciveFilesButton = builder.get_object("ReciveFilesButton")
        self.LogOutButton = builder.get_object("LogOutButton")
        
        for exitnode in list(TS.Use_json()["ExitNodes"].keys()):
            T_exitnode = Adw.ActionRow(
            title=exitnode,
            activatable=True
            )
            T_exitnode.connect("activated", self.on_exit_node_clicked)
            self.ExitNodesList.append(T_exitnode)
        
        
        
        self.refresh_app()
        
        self.window = builder.get_object("mainWindow")
        self.window.set_application(self)  
        self.window.present()

    def show_window(self):
        self.window.present()
        
    def on_exit_node_clicked(self,widget):
        
        self.selected_exit_node = widget.get_title()
        
        if self.selected_exit_node == 'None':
            TS.setExitNode("off")
        else:
            TS.setExitNode(self.selected_exit_node)
        
        TS.Use_json({"UsedExitNode": self.selected_exit_node}) # Persist the choice
        print(f"Selected exit node: {self.selected_exit_node}")
        self.refresh_app()

app = GtkGUI(application_id="com.example.TailscaleGUI")
app.run(sys.argv)

