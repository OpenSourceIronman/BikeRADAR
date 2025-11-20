#!/usr/bin/env python

from nicegui import ui

DEBUG_STATEMENTS_ON = True

class KeyBoard:

    layout = []


    def __init__(self):
        self.keys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'DELETE','TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','[', ']', '\\', 'CAPS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'ENTER', 'SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'R SHIFT']
        self.shiftToggle = False
        self.capsToggle = False
        self.currentPressedKey = ''
        self.textInput = ''

    def type_key(self, key):
        if DEBUG_STATEMENTS_ON: print(f"KEY: {self.currentPressedKey}")

        if key == 'DELETE':
            self.textInput = self.textInput[:-1]

        if key == 'DELETE' or key == 'SHIFT' or key == 'R SHIFT' or key == 'CAPS' or key == '^^^^' or key == 'ENTER' or key == 'TAB':
            pass
        else:
            self.textInput = self.textInput + key

        if DEBUG_STATEMENTS_ON: print(self.textInput)


    def key_2nd_option(self, key):
        switch = {
            '`': '~',
            '1': '!',
            '2': '@',
            '3': '#',
            '4': '$',
            '5': '%',
            '6': '^',
            '7': '&',
            '8': '*',
            '9': '(',
            '0': ')',
            '-': '_',
            '=': '+',
            '[': '{',
            ']': '}',
            '\\': '|',
            ';': ':',
            "'": '"',
            ',': '<',
            '.': '>',
            '/': '?',
            'SHIFT': 'SHIFT',
            'R SHIFT': 'R SHIFT',
            'DELETE': 'DELETE',
            'ENTER':'ENTER',
            'CAPS': '^^^^'
        }

        return switch[key]

    def button_pressed(self, key):
        global layout

        if key == 'CAPS' or key == '^^^^':
            if not self.capsToggle:
                self.capsToggle = True
                KeyBoard.layout[28].set_text('^^^^')
            elif self.capsToggle:
                self.capsToggle = False
                KeyBoard.layout[28].set_text('CAPS')


        if (key == 'SHIFT' or key == 'R SHIFT') and not self.shiftToggle:

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

            KeyBoard.layout[49].set_text('<')
            KeyBoard.layout[50].set_text('>')
            KeyBoard.layout[51].set_text('?')

            self.shiftToggle = True
            self.currentPressedKey = key

        elif self.shiftToggle:

            # Try / Exception handling reduces the size of switch dictionary in the key_2nd_option() function
            try:
                self.currentPressedKey = self.key_2nd_option(key)
            except KeyError:
                self.currentPressedKey = key.upper()

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

            KeyBoard.layout[49].set_text(',')
            KeyBoard.layout[50].set_text('.')
            KeyBoard.layout[51].set_text('/')

            self.shiftToggle = False

        else:
            self.currentPressedKey = key

        if self.capsToggle:
            self.currentPressedKey = key.upper()

        self.type_key(self.currentPressedKey)

    def gui(self):
        global text
        with ui.row().classes('gap-[5px] w-[705px]'):
            for key in qwerty.keys:
                if key == '\\':
                    css = 'w-[71px]'
                elif key == 'SHIFT':
                    css = 'w-[85px]'
                elif key == 'R SHIFT':
                    css = 'w-[140px]'
                elif  key == 'ENTER':
                    css = 'w-[108px]'
                else:
                    css = ''

                KeyBoard.layout.append(ui.button(key, on_click=lambda e: qwerty.button_pressed(e.sender.text))
                                    .style('font-family: "Courier New", monospace; font-weight: bold; font-size: 16px;')
                                    .classes('!bg-blue-900' + ' ' + css))

        text = ui.label('')


if __name__ in {"__main__", "__mp_main__"}:
    qwerty = KeyBoard()
    qwerty.gui()

    ui.run(title='Virtual Keyboard', native=True, dark=True, window_size=(900, 300))
