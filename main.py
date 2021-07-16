import PySimpleGUIQt as sg

menu_layout = [
    ['File', ['Open', '---', 'Exit']]
]

treeData = sg.TreeData()
tree = sg.Tree(data=treeData, show_expanded=True, key='TREE', headings=[], num_rows=20)
editor = sg.Multiline()

window_layout = [
    [sg.Menu(menu_layout)],
    [
        tree,
        editor
    ]
]

window = sg.Window('pycDisGUI', window_layout, resizable=False)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break