import serial
import time
from Tkinter import *

###
# configuration
###

# only mac is currently supported
OS = 'mac'

# tty for Bluetooth device with baud
SERIAL_TERMINAL = '/dev/tty.VIRTKEY-DevB'
BAUD = 2400

# connect and transmit to serial device?
TRANSMIT = False

# font size for GUI
FONT_SIZE = 16

###
# end configuration
###


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

special_mappings = {
    # ctrl-0 to cmd-space
    ('0', ('<C>',)): (' ', ('<M>',))
}

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

# Mask on event.state
#####
# 0x0001	Shift.
# 0x0002	Caps Lock.
# 0x0004	Control.
# 0x0008	Left-hand Alt.
# 0x0010	Num Lock.
# 0x0080	Right-hand Alt.
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

def set_to_tuple(s):
    return tuple(list(s))

def translate_keys(key, modifiers):
    current_combo = (key, set_to_tuple(modifiers))
    # print current_combo
    if current_combo in special_mappings:
        translation = special_mappings[current_combo]
        print 'translating {} to {}'.format(current_combo, translation)
        return translation
    return (key, modifiers)

def encode(key, modifiers):
    key, modifiers = translate_keys(key, modifiers)
    n_pressed = len(modifiers) + (0 if key == '' else 1)
    modifier_string = ''.join(modifiers)
    return '{}{}{}'.format(n_pressed, modifier_string, key)

class KeyHandler():
    def __init__(self, parent, ser, status_label):
        self.parent = parent
        self.parent.bind("<Key>", self.keypress)
        self.status_label = status_label

        self.ser = ser

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
            print "writing: '{}'".format(x)
            if self.ser is not None:
                self.ser.write(x)
        time.sleep(1 / 1000000)
        self.parent_insert(event.char)
        self.status_label.set(encoding)

# begin main
root = Tk()
root.wm_title('replay keys')

frame = Frame(root, width = 400, height = 300)
frame.pack(fill = BOTH, expand = True)

text_box = Text(frame, font = ("Helvetica", FONT_SIZE))
text_box.config(state = DISABLED)
text_box.focus_set()
text_box.grid(row = 0, rowspan = 5)

status_text = StringVar()

label = Label(frame, textvariable = status_text, font = ("Helvetica", FONT_SIZE))

label.grid(row = 5, rowspan = 1)

status_text.set('No keys transmitted yet.')

if TRANSMIT:
    with serial.Serial(SERIAL_TERMINAL, BAUD) as ser:
        key_handler = KeyHandler(text_box, ser, status_text)
        root.mainloop()
else:
    key_handler = KeyHandler(text_box, None, status_text)
    root.mainloop()
