from xdis_parse import XdisBytecode
import gi
import webbrowser


def main():
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    builder = Gtk.Builder()
    builder.add_from_file("gui.glade")
    window = builder.get_object("window1")

    global bytecodeFile
    global codeTreeStore
    global codeBrowserBuffer
    global codeTree
    global menu_linenum
    global menu_jumps
    bytecodeFile = None
    codeTree = builder.get_object("code_tree")
    codeTreeStore = builder.get_object("code_tree_store")
    codeBrowserBuffer = builder.get_object("bytecode_buffer")
    menu_linenum = builder.get_object("menu_view_linenum")
    menu_jumps = builder.get_object("menu_view_targets")

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
                global bytecodeFile
                global codeTreeStore
                global codeBrowserBuffer
                global codeTree
                global menu_linenum
                global menu_jumps
                codeTreeStore.clear()
                bytecodeFile = XdisBytecode.from_file(dialog.get_filename())
                tree_stack = []
                treefile = codeTreeStore.append(None, [bytecodeFile.name])
                tree_stack.append(treefile)

                def recurse(bytecode:XdisBytecode, stack:list):
                    for i in bytecode.sub:
                        stack.append(codeTreeStore.append(stack[-1], [i.name]))
                        recurse(i, stack)
                        stack.pop()

                recurse(bytecodeFile, tree_stack)
                codeTree.expand_all()
                codeBrowserBuffer.set_text(bytecodeFile.get_bytecode(linenum=menu_linenum.get_active(), jumps=menu_jumps.get_active()))
            dialog.destroy()

        def code_tree_cursor_changed(self, data):
            store, iter = data.get_selection().get_selected()
            if iter == None:
                return
            path = store.get_string_from_iter(iter)
            path = list(map(int, path.split(':')))[1:]
            global bytecodeFile
            global codeBrowserBuffer
            bytecode = bytecodeFile
            for i in path:
                bytecode = bytecode.sub[i]
            codeBrowserBuffer.set_text(bytecode.get_bytecode(linenum=menu_linenum.get_active(), jumps=menu_jumps.get_active()))

        def menu_help_dis_activate(self, data):
            webbrowser.open("https://docs.python.org/3/library/dis.html")

        def menu_view_toggled(self, data):
            store, iter = codeTree.get_selection().get_selected()
            global bytecodeFile
            global codeBrowserBuffer
            if iter == None:
                if bytecodeFile:
                    codeBrowserBuffer.set_text(bytecodeFile.get_bytecode(linenum=menu_linenum.get_active(), jumps=menu_jumps.get_active()))
                return
            path = store.get_string_from_iter(iter)
            path = list(map(int, path.split(':')))[1:]
            bytecode = bytecodeFile
            for i in path:
                bytecode = bytecode.sub[i]
            codeBrowserBuffer.set_text(bytecode.get_bytecode(linenum=menu_linenum.get_active(), jumps=menu_jumps.get_active()))


    builder.connect_signals(Handler())
    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()