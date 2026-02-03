#!/usr/bin/env python

from nicegui import ui


class Constant:
    QWERTY = 1
    DVORAK = 2
    WINDOWS = 3
    MAC = 4
    DEBUG_STATEMENTS_ON = False
    CAPS_LOCK_ON = 'CAPS_LOCK_ON'
    MIN_WINDOW_SIZE = (1080, 300)

class KeyBoard:

    layout = []
    CAPS_LAYOUT_POS = 28
    L_SHIFT_LAYOUT_POS = 41
    R_SHIFT_LAYOUT_POS = 52

    def __init__(self, type: Constant, os: Constant = None):
        if type == Constant.QWERTY:
            self.keys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'DELETE','TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','[', ']', '\\', 'CAPS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'ENTER', 'SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'SHIFT', '🌐']
        #elif type == Constant.DVORAK:
            #self.keys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '[', ']', 'DELETE','TAB', "'", ',', '.', 'p', 'y', 'f', 'g', 'c', 'r', 'l', '/', '=', '\\', 'CAPS', 'a', 'o', 'e', 'u', 'i', 'd', 'h', 't', 'n', 's', '-', 'ENTER', 'SHIFT', ';', 'q','j', 'k', 'x', 'b', 'm', 'w', 'v', 'z', 'R SHIFT']

        if os == None:
            pass
        elif os == Constant.WINDOWS:
            winKeys = ['CTRL', 'WIN', 'ALT', 'SPACE', 'ALT', 'SUP', 'CTRL']
            for key in winKeys:
                self.keys.append(key)
        elif os == Constant.MAC:
            macKeys = ['CTRL', 'OPT', 'CMD', 'SPACE', 'CMD', 'OPT', 'CTRL']
            for key in macKeys:
                self.keys.append(key)

        self.shiftToggleOn = False
        self.capsToggleOn = False

        self.modifierKeyToggleOn = {'CTRL': False, 'WIN': False, 'ALT': False, 'OPT': False, 'CMD': False, 'SUP': False}
        self.shortcut = ''

        self.currentPressedKey = ''
        self.textInput = ''


    def type_key(self, key):
        """ Store typeable keys to self.textInput

        Args:
            key (str): The key to type

        """
        if Constant.DEBUG_STATEMENTS_ON: print(f"KEY: {self.currentPressedKey}")

        if key == 'DELETE':
            self.textInput = self.textInput[:-1]
        elif key == 'ENTER':
            self.textInput = self.textInput + '\n'
        elif key == 'SPACE':
            self.textInput = self.textInput + ' '
        elif key == 'TAB':
            self.textInput = self.textInput + '\t'
        elif key == 'SHIFT' or key == 'CAPS' or key == Constant.CAPS_LOCK_ON:
            pass
        else:
            self.textInput = self.textInput + key

        print(f"TEXT: {self.textInput}")


    def key_2nd_option(self, key) -> str:
        """ Define the 2nd character option for a key

        Args:
            key (str): Key to get the 2nd character options for

        Returns:
            str: The 2nd character option for a key
        """
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
            'DELETE': 'DELETE',
            'ENTER':'ENTER',
            'CAPS': Constant.CAPS_LOCK_ON
        }

        return switch[key]


    def catch_modifier_keys(self, key):
        for modifierKey in self.modifierKeyToggleOn:
            if self.modifierKeyToggleOn[modifierKey]:
                self.shortcut = modifierKey + key
                self.modifierKeyToggleOn[modifierKey] = False

        print(f"SHORTCUT: {self.shortcut}")

        #try:
        #    self.modifierKeyToggleOn[key] = True
        #except KeyError:
        #   pass


    def button_pressed(self, key):
        global layout

        if key == 'CTRL' or key == 'WIN' or key == 'ALT' or key == 'SUP' or key == 'OPT' or key == 'CMD':
            self.modifierKeyToggleOn[key] = True

        if key == 'CAPS':
            if not self.capsToggleOn:
                self.capsToggleOn = True
                KeyBoard.layout[KeyBoard.CAPS_LAYOUT_POS].classes('!bg-red-900')
            elif self.capsToggleOn:
                self.capsToggleOn = False
                KeyBoard.layout[KeyBoard.CAPS_LAYOUT_POS].classes(remove='!bg-red-900')

        elif key == 'SHIFT' and not self.shiftToggleOn:

            KeyBoard.layout[KeyBoard.L_SHIFT_LAYOUT_POS].classes('!bg-red-900')
            KeyBoard.layout[KeyBoard.R_SHIFT_LAYOUT_POS].classes('!bg-red-900')

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

            self.shiftToggleOn = True
            self.currentPressedKey = key

        elif self.shiftToggleOn:

            # Try / Exception handling reduces the size of switch dictionary in the key_2nd_option() function
            try:
                self.currentPressedKey = self.key_2nd_option(key)
            except KeyError:
                self.currentPressedKey = key.upper()

            KeyBoard.layout[KeyBoard.L_SHIFT_LAYOUT_POS].classes(remove='!bg-red-900')
            KeyBoard.layout[KeyBoard.R_SHIFT_LAYOUT_POS].classes(remove='!bg-red-900')

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

            self.shiftToggleOn = False

        else:
            self.currentPressedKey = key


        if self.capsToggleOn:
            self.currentPressedKey = key.upper()

        if key == '🌐':
            emojiButtons.visible = not emojiButtons.visible
        else:
            self.type_key(self.currentPressedKey)
            self.shortcut = ''


    def gui(self):
        global emojiButtons

        with ui.row().classes('gap-4'):

            with ui.column().classes('gap-2'):
                with ui.row().classes('gap-[5px] w-[705px]'):
                    for key in qwerty.keys:
                        if key == '\\':
                            css = 'w-[71px]'
                        elif key == 'SHIFT':
                            css = 'w-[83px]'
                        elif key == 'R SHIFT':
                            css = 'w-[140px]'
                        elif key == 'ENTER':
                            css = 'w-[108px]'
                        elif key == 'SPACE':
                            css = 'w-[281px]'
                        else:
                            css = ''

                        KeyBoard.layout.append(ui.button(key, on_click=lambda e: qwerty.button_pressed(e.sender.text))
                                            .style('font-family: "Courier New", monospace; font-weight: bold; font-size: 16px;')
                                            .classes('!bg-blue-900' + ' ' + css))

            with ui.column():
                with ui.grid(columns=6).classes("gap-[5px]") as emojiButtons:
                    for emoji in ["😀","😊","😎","😍","🥰","😘",
                                  "🥺","🥹","🤔","😭","😔","🫠",
                                  "💀","😂","🤣","🙏","🫶","👍",
                                  "✅","❤️","❤️‍🩹","💔","🔥","🎉",
                                  "🎄","⭐","🎅","🤶","❄️","🎁"]:
                        ui.button(emoji, on_click=lambda e: qwerty.button_pressed(e.sender.text)).style('font-family: "Courier New", monospace; font-weight: bold; font-size: 16px;').classes('!bg-blue-900 w-[40px] h-[40px] ')

if __name__ in {"__main__", "__mp_main__"}:
    qwerty = KeyBoard(Constant.QWERTY, Constant.MAC)
    qwerty.gui()
    ui.run(title='Virtual Keyboard', native=True, dark=True, window_size=Constant.MIN_WINDOW_SIZE)
