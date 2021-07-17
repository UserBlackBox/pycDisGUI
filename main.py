from xdis_parse import XdisBytecode
import gi


def main():
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    builder = Gtk.Builder()
    builder.add_from_file("gui.glade")
    window = builder.get_object("window1")

    bytecodeFile = None
    codeTreeStore = builder.get_object("code_tree_store")

    class Handler:
        def window1_onDestroy(self, *args):
            Gtk.main_quit()

        def menu_file_quit_activate(self, *args):
            Gtk.main_quit()

        def menu_file_open_activate(self, *args):
            dialog = Gtk.FileChooserDialog(title="Open", parent=window, action=Gtk.FileChooserAction.OPEN)
            dialog.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            )
            filter_pyc = Gtk.FileFilter()
            filter_pyc.set_name("Python Bytecode file")
            filter_pyc.add_mime_type("application/x-python-bytecode")
            dialog.add_filter(filter_pyc)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                bytecodeFile = XdisBytecode.from_file(dialog.get_filename())
            dialog.destroy()

    builder.connect_signals(Handler())
    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()