import PySimpleGUIQt as sg

sg.theme('Default')

def main_window():
    menu_layout = [
        ['File', ['Open', '---', 'Exit']]
    ]

    window_layout = [
        [sg.Menu(menu_layout)],
        [sg.Listbox(values=[]), sg.Multiline()]
    ]

    window = sg.Window('pycDisGUI', window_layout, resizable=True)
    return window

window = main_window()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break