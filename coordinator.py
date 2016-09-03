import serial
import time
from Tkinter import *

SERIAL_TERMINAL = '/dev/tty.VIRTKEY-DevB'
BAUD = 2400
OS = 'mac'

root = Tk()

# Mask on event.state
#####
# 0x0001	Shift.
# 0x0002	Caps Lock.
# 0x0004	Control.
# 0x0008	Left-hand Alt.
# 0x0010	Num Lock.
# 0x0080	Right-hand Alt.

# Keys on Arduino
#####
# Key	Hexadecimal value	Decimal value
# KEY_LEFT_CTRL	0x80	128
# KEY_LEFT_SHIFT	0x81	129
# KEY_LEFT_ALT	0x82	130
# KEY_LEFT_GUI	0x83	131
# KEY_RIGHT_CTRL	0x84	132
# KEY_RIGHT_SHIFT	0x85	133
# KEY_RIGHT_ALT	0x86	134
# KEY_RIGHT_GUI	0x87	135
# KEY_UP_ARROW	0xDA	218
# KEY_DOWN_ARROW	0xD9	217
# KEY_LEFT_ARROW	0xD8	216
# KEY_RIGHT_ARROW	0xD7	215
# KEY_BACKSPACE	0xB2	178
# KEY_TAB	0xB3	179
# KEY_RETURN	0xB0	176
# KEY_ESC	0xB1	177
# KEY_INSERT	0xD1	209
# KEY_DELETE	0xD4	212
# KEY_PAGE_UP	0xD3	211
# KEY_PAGE_DOWN	0xD6	214
# KEY_HOME	0xD2	210
# KEY_END	0xD5	213
# KEY_CAPS_LOCK	0xC1	193
# KEY_F1	0xC2	194
# KEY_F2	0xC3	195
# KEY_F3	0xC4	196
# KEY_F4	0xC5	197
# KEY_F5	0xC6	198
# KEY_F6	0xC7	199
# KEY_F7	0xC8	200
# KEY_F8	0xC9	201
# KEY_F9	0xCA	202
# KEY_F10	0xCB	203
# KEY_F11	0xCC	204
# KEY_F12	0xCD	205

special_characters = {
    'Up': '<u>',
    'Down': '<d>',
    'Left': '<l>',
    'Right': '<r>',
    'BackSpace': '<b>',
    'Tab': '<t>',
    'Return': '<R>',
    'Escape': '<e>',
    # TODO: insert
    'Delete': '<D>',
    'Prior': '<U>', # page up
    'Next': '<n>', # page down
    'Home': '<h>',
    'End': '<E>',
    # TODO: caps lock
}
# insert the F keys
for i in range(1, 10):
    key = 'F{}'.format(i)
    special_characters[key] = '<{}>'.format(i)
# ASCII 10, 11, 12
special_characters['F10'] = '<:>'
special_characters['F11'] = '<;>'
special_characters['F12'] = '<<>'
# print(special_characters)

def is_alt(s):
    if OS == 'mac':
        return (s & 0x10) != 0
def is_command(s):
    if OS == 'mac':
        return (s & 0x8) != 0 or (s & 0x80) != 0
def get_modifiers(s):
    modifiers = set()
    ctrl  = (s & 0x4) != 0
    # for some reason these don't work on mac is they are supposed to
    alt = is_alt(s)
    command = is_command(s)
    # alt   = (s & 0x8) != 0 or (s & 0x80) != 0
    shift = (s & 0x1) != 0
    # number_lock = (s & 0x10) != 0
    caps_lock = (s & 0x2) != 0
    if ctrl:
        modifiers.add('<C>')
    if alt:
        modifiers.add('<A>')
    if shift:
        modifiers.add('<S>')
    if command:
        modifiers.add('<M>')
    # if number_lock:
    #     modifiers.add('num_lock')
    # if caps_lock:
    #     modifiers.add('caps_lock')
    return modifiers
def get_key(event):
    symbol = event.keysym
    # print 'event.char "{}" "{}" "{}" "{}"'.format(event.char, repr(event.char), len(event.char), symbol)
    if symbol in special_characters:
        # print 'symbol: {}'.format(symbol)
        return special_characters[symbol]
    # elif len(event.char) == 0:
    #     return ''
    elif len(symbol) == 1:
        return symbol
    elif len(event.char) == 1:
        # print 'lower: {}'.format(event.char.lower())
        return event.char
    else:
        return 'ERROR'

def encode(key, modifiers):
    n_pressed = len(modifiers) + (0 if key == '' else 1)
    modifier_string = ''.join(modifiers)
    return '{}{}{}'.format(n_pressed, modifier_string, key)

class KeyHandler():
    def __init__(self, parent, ser):
        self.parent = parent
        self.parent.bind("<Key>", self.keypress)

        # set the state to be disabled so we don't get weird special characters
        self.parent.config(state = DISABLED)

    def parent_insert(self, c):
        self.parent.config(state = NORMAL)
        self.parent.insert(END, c)
        self.parent.config(state = DISABLED)

    def keypress(self, event):
        if len(event.char) == 0:
            return
        # print repr(event.char)
        modifiers = get_modifiers(event.state)
        key = get_key(event)
        encoding = encode(key, modifiers)
        print encoding

        for x in encoding:
            print 'writing: ', x
            ser.write(x)
        time.sleep(1 / 1000000)
        self.parent_insert(event.char)

frame = Frame(root, width = 400, height = 300)
frame.pack(fill=BOTH, expand=True)

text_box = Text(frame, font=("Helvetica", 16))
text_box.config(state = DISABLED)
text_box.focus_set()
text_box.grid(row = 0, rowspan = 5)

v = StringVar()

label = Label(frame, textvariable = v, font=("Helvetica", 16))

label.grid(row = 5, rowspan = 1)

# TODO: pass this into KeyHandler and update with the latest key sent
v.set('hello')

# text_box.bind("<Key>", lambda e: key(e, v))

with serial.Serial(SERIAL TERMINAL, BAUD) as ser:
    key_handler = KeyHandler(text_box, ser)
    root.mainloop()
