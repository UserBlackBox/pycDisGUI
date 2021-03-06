from xdis_parse import XdisBytecode
import gi
import webbrowser


def main():
    gi.require_version("Gtk", "3.0")
    gi.require_version("GtkSource", '4')
    from gi.repository import Gtk, GtkSource, GObject
    from os.path import abspath, dirname, join

    builder = Gtk.Builder()
    GObject.type_register(GtkSource.View)
    GObject.type_register(GtkSource.Buffer)
    GObject.type_register(GtkSource.LanguageManager)
    GObject.type_register(GtkSource.Language)
    GObject.type_register(GtkSource.StyleSchemeChooserButton)
    builder.add_from_file(join(abspath(dirname(__file__)), "main.glade"))
    window = builder.get_object("window1")

    global bytecodeFile
    global codeTreeStore
    global codeBrowserBuffer
    global codeTree
    global menu_linenum
    global menu_jumps
    global details_buffer
    global constants_buffer
    bytecodeFile = None
    codeTree = builder.get_object("code_tree")
    codeTreeStore = builder.get_object("code_tree_store")
    codeBrowserBuffer = builder.get_object("bytecode_buffer")
    menu_linenum = builder.get_object("menu_view_linenum")
    menu_jumps = builder.get_object("menu_view_targets")
    details_buffer = builder.get_object("details_buffer")
    constants_buffer = builder.get_object("constants_buffer")

    langmanager = GtkSource.LanguageManager()
    lang = langmanager.get_language('python3')
    codeBrowserBuffer.set_language(lang)
    constants_buffer.set_language(lang)

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
                window.set_title("pycDisGUI - {}".format(dialog.get_filename().split('/')[-1]))
                tree_stack = []
                treefile = codeTreeStore.append(None, [bytecodeFile.filename])
                tree_stack.append(treefile)

                def recurse(bytecode:XdisBytecode, stack:list):
                    for i in bytecode.sub:
                        stack.append(codeTreeStore.append(stack[-1], [i.name]))
                        recurse(i, stack)
                        stack.pop()

                recurse(bytecodeFile, tree_stack)
                codeTree.expand_all()
                codeTree.set_cursor(Gtk.TreePath.new_first())
                start = codeBrowserBuffer.get_start_iter()
                end = codeBrowserBuffer.get_end_iter()
                codeBrowserBuffer.delete(start, end)
                text = bytecodeFile.get_bytecode(linenum=menu_linenum.get_active(),
                                                 jumps=menu_jumps.get_active())
                codeBrowserBuffer.insert_markup(start, text, len(text))

                global details_buffer
                start = details_buffer.get_start_iter()
                end = details_buffer.get_end_iter()
                details_buffer.delete(start, end)
                text = bytecodeFile.get_details()
                details_buffer.insert_markup(start, text, len(text))

                global constants_buffer
                constants_buffer.set_text(bytecodeFile.get_consts())

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
            start = codeBrowserBuffer.get_start_iter()
            end = codeBrowserBuffer.get_end_iter()
            codeBrowserBuffer.delete(start,end)
            text = bytecode.get_bytecode(linenum=menu_linenum.get_active(),
                                             jumps=menu_jumps.get_active())
            codeBrowserBuffer.insert_markup(start, text, len(text))

            global details_buffer
            start = details_buffer.get_start_iter()
            end = details_buffer.get_end_iter()
            details_buffer.delete(start, end)
            text = bytecode.get_details()
            details_buffer.insert_markup(start, text, len(text))

            global constants_buffer
            constants_buffer.set_text(bytecode.get_consts())

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
            start = codeBrowserBuffer.get_start_iter()
            end = codeBrowserBuffer.get_end_iter()
            codeBrowserBuffer.delete(start,end)
            text = bytecode.get_bytecode(linenum=menu_linenum.get_active(),
                                         jumps=menu_jumps.get_active())
            codeBrowserBuffer.insert_markup(start, text, len(text))


    builder.connect_signals(Handler())
    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()