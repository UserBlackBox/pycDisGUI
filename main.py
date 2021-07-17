from xdis_parse import xdisBytecode
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

builder = Gtk.Builder()
builder.add_from_file("gui.glade")

class Handler:
    def onDestroy(self, *args):
        Gtk.main_quit()

builder.connect_signals(Handler())

window = builder.get_object("window1")
window.show_all()
Gtk.main()