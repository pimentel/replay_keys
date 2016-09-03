#include "Keyboard.h"

void setup() {

  // connect to bluetooth device
  Serial1.begin(2400);
  while (!Serial1) {
    ;
  }

  // connect to serial device to output print
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }

  // initialize control over the keyboard:
  Keyboard.begin();
}

char special_lookup(char c) {
  switch(c){
    case 'C':
      return KEY_LEFT_CTRL;
    case 'S':
      return KEY_LEFT_SHIFT;
    case 'A':
      return KEY_LEFT_ALT;
    case 'M':
      return KEY_LEFT_GUI;
    case 'u':
      return KEY_UP_ARROW;
    case 'd':
      return KEY_DOWN_ARROW;
    case 'l':
      return KEY_LEFT_ARROW;
    case 'r':
      return KEY_RIGHT_ARROW;
    case 'b':
      return KEY_BACKSPACE;
    case 't':
      return KEY_TAB;
    case 'R':
      return KEY_RETURN;
    case 'e':
      return KEY_ESC;
//    TODO: insert
    case 'D':
      return KEY_DELETE;
    case 'U':
      return KEY_PAGE_UP;
    case 'n':
      return KEY_PAGE_DOWN;
    case 'h':
      return KEY_HOME;
    case 'E':
      return KEY_END;
    case '1':
    case '2':
    case '3':
    case '4':
    case '5':
    case '6':
    case '7':
    case '8':
    case '9':
    case ':': // ascii 10, 11, 12
    case ';':
    case '<':
      // F keys. F1 starts at 193 decimal
      return 193 + int(c - '0');    
    default:
      // upon error, enter a '?'
      return '?';
  }
}

char safe_read() {
  // use a spinlock to ensure that a byte is always read
  while (!Serial1.available()) {
    ;
  }

  return Serial1.read();
}

char get_character() {
  char next;
  
  next = safe_read();

  if (next == '<') {
    // the next character is a special character
    next = safe_read();
    next = special_lookup(next);
    // discard the closing '>'
    safe_read();
  }

  Serial.print(next, DEC);
  Serial.print(" : ");
  Serial.print(next);
  Serial.print("\n\r");
  return next;
}
  
void loop() {
  char incoming;
  int n_keys = 0;

  while (Serial1.available() > 0) {
    n_keys = safe_read() - '0';

    Serial.print("n_keys remaining: ");
    Serial.print(n_keys);
    Serial.print("\n\r");
    while (n_keys) {
      incoming = get_character();
      Keyboard.press(incoming);
      --n_keys;
    }
    delay(10);
    Keyboard.releaseAll();
    delay(10);

  }
}

