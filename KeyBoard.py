#!/usr/bin/env python

from nicegui import ui

class KeyBoard:

    layout = []
    shiftPressed = False
    capsToggle = False

    qwertyStackedPositions = {}

    # ` 1 2 3 4 5 6 7 8 9 0 - =
    # Q W E R T Y U I O P [ ] \
    #  A S D F G H J K L ; '
    #   Z X C V B N M , . /
    # Ctrl Option Command Space Command Option Ctrl

    # The total width is 720 x 180, with 5 px spacing between keys, with ALL keys with absolute coordinates  from upper left which is (0, 0)
    qwertyStaggeredPositions = {
      "`": [20, 20],
      "1": [65, 20],
      "2": [110, 20],
      "3": [155, 20],
      "4": [200, 20],
      "5": [245, 20],
      "6": [290, 20],
      "7": [335, 20],
      "8": [380, 20],
      "9": [425, 20],
      "0": [470, 20],
      "-": [515, 20],
      "=": [560, 20],
      "DELETE": [605, 20],

      "Q": [40, 65],
      "W": [85, 65],
      "E": [130, 65],
      "R": [175, 65],
      "T": [220, 65],
      "Y": [265, 65],
      "U": [310, 65],
      "I": [355, 65],
      "O": [400, 65],
      "P": [445, 65],
      "[": [490, 65],
      "]": [535, 65],
      "\\_": [580, 65],

      "A": [55, 110],
      "S": [100, 110],
      "D": [145, 110],
      "F": [190, 110],
      "G": [235, 110],
      "H": [280, 110],
      "J": [325, 110],
      "K": [370, 110],
      "L": [415, 110],
      ";": [460, 110],
      "'": [505, 110],
      "ENTER": [550, 110],

      "Z": [70, 155],
      "X": [115, 155],
      "C": [160, 155],
      "V": [205, 155],
      "B": [250, 155],
      "N": [295, 155],
      "M": [340, 155],
      ",": [385, 155],
      ".": [430, 155],
      "/": [475, 155],

      "Space": [360, 155]
    }



    def __init__(self):
        self.keys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'DELETE','TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','[', ']', '\\', 'CAPS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'ENTER', 'SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'R SHIFT']
        self.totalKeys = len(self.keys)

        self.keyWidth = 40
        self.keyHeight = 40
        self.rowLengths = [14]
        self.rowOffset = [20, 30, 45]
        self.currentPressedKey = ''


    def button_pressed(self, key):
        global layout, shiftPressed, capsToggle

        self.currentPressedKey = key


        if key == 'CAPS':
            if not KeyBoard.capsToggle:
                KeyBoard.capsToggle = True
                KeyBoard.layout[28].set_text('^^^^')
            else:
                KeyBoard.capsToggle = False
                KeyBoard.layout[28].set_text('CAPS')


        if (key == 'SHIFT' or key == 'R SHIFT') and not KeyBoard.shiftPressed:
            KeyBoard.shiftPressed = True
            KeyBoard.layout[0].set_text('~')
            KeyBoard.layout[1].set_text('!')
            KeyBoard.layout[2].set_text('@')
            KeyBoard.layout[3].set_text('#')
            KeyBoard.layout[4].set_text('$')
            KeyBoard.layout[5].set_text('%')
            KeyBoard.layout[6].set_text('^')
            KeyBoard.layout[7].set_text('&')
            KeyBoard.layout[8].set_text('*')
            KeyBoard.layout[9].set_text('(')
            KeyBoard.layout[10].set_text(')')
            KeyBoard.layout[11].set_text('_')
            KeyBoard.layout[12].set_text('+')

            KeyBoard.layout[25].set_text('{')
            KeyBoard.layout[26].set_text('}')
            KeyBoard.layout[27].set_text('|')

            KeyBoard.layout[38].set_text(':')
            KeyBoard.layout[39].set_text('"')
        else:
            KeyBoard.shiftPressed = False
            KeyBoard.layout[0].set_text('`')
            KeyBoard.layout[1].set_text('1')
            KeyBoard.layout[2].set_text('2')
            KeyBoard.layout[3].set_text('3')
            KeyBoard.layout[4].set_text('4')
            KeyBoard.layout[5].set_text('5')
            KeyBoard.layout[6].set_text('6')
            KeyBoard.layout[7].set_text('7')
            KeyBoard.layout[8].set_text('8')
            KeyBoard.layout[9].set_text('9')
            KeyBoard.layout[10].set_text('0')
            KeyBoard.layout[11].set_text('-')
            KeyBoard.layout[12].set_text('=')

            KeyBoard.layout[25].set_text('[')
            KeyBoard.layout[26].set_text(']')
            KeyBoard.layout[27].set_text('\\')

            KeyBoard.layout[38].set_text(';')
            KeyBoard.layout[39].set_text("'")

        if KeyBoard.capsToggle:
            self.currentPressedKey = key.upper()

        print(f"Key {self.currentPressedKey} pressed")

if __name__ in {"__main__", "__mp_main__"}:
    qwerty = KeyBoard()


    for i in qwerty.rowLengths:
        with ui.row().classes('gap-[5px]'):
            for key in qwerty.keys:
                if key == '\\':
                    css = 'w-[65px]'
                elif key == 'SHIFT':
                    css = 'w-[85px]'
                elif key == 'R SHIFT':
                    css = 'w-[128px]'
                elif  key == 'ENTER':
                    css = 'w-[102px]'
                else:
                    css = None

                KeyBoard.layout.append(ui.button(key, on_click=lambda key=key: qwerty.button_pressed(key)).style('font-family: "Courier New", monospace;').classes(css))

    #print(KeyBoard.layout[2])
    #print(KeyBoard.qwertyStaggeredPositions["Q"])

    ui.run(title='Virtual Keyboard', native=True, dark=True, window_size=(705, 260))
