import display
import vgr2d
import fpga

display.SPACE_WIDTH = 1
display.FONT_HEIGHT = 48
display.FONT_WIDTH = 23 + display.SPACE_WIDTH
WIDTH   = 640
HEIGHT  = 400
SPACE_WIDTH = 1
FONT_HEIGHT = 48
FONT_WIDTH = 23 + SPACE_WIDTH

TOP_LEFT        = 1
MIDDLE_LEFT     = 2
BOTTOM_LEFT     = 3
TOP_CENTER      = 4
BOTTOM_CENTER   = 5
TOP_RIGHT       = 6
MIDDLE_CENTER   = 7
MIDDLE_RIGHT    = 8
BOTTOM_RIGHT    = 9

Colored = display.Colored

class Text(Colored):
  def __init__(self, string, x, y, color, justify=TOP_LEFT):
    self.x = int(x)
    self.y = int(y)
    self.string = string
    self.col = color
    self.justify(justify)

  def __repr__(self):
    return f"Text('{self.string}', {self.x}, {self.y}, {self.col})"

  def justify(self, justify):
    left = (TOP_LEFT, MIDDLE_LEFT, BOTTOM_LEFT)
    center = (TOP_CENTER, MIDDLE_CENTER, BOTTOM_CENTER)
    right = (TOP_RIGHT, MIDDLE_RIGHT, BOTTOM_RIGHT)

    if justify in left:
      self.x = self.x
    elif justify in center:
      self.x = self.x - self.width(self.string) // 2
    elif justify in right:
      self.x = self.x - self.width(self.string)
    else:
      raise ValueError('unknown justify value')

    top = (TOP_LEFT, TOP_CENTER, TOP_RIGHT)
    middle = (MIDDLE_LEFT, MIDDLE_CENTER, MIDDLE_RIGHT)
    bottom = (BOTTOM_LEFT, BOTTOM_CENTER, BOTTOM_RIGHT)

    if justify in top:
      self.y = self.y
    elif justify in middle:
      self.y = self.y - FONT_HEIGHT // 2
    elif justify in bottom:
      self.y = self.y - FONT_HEIGHT
    else:
      raise ValueError('unknown justify value')

  def width(self, string):
    return FONT_WIDTH * len(string)

  def clip_x(self):
    string = self.string
    x = self.x

    if x < 0:
      i = abs(x) // FONT_WIDTH + 1
      string = string[i:]
      x += i * FONT_WIDTH
    if x + self.width(string) > WIDTH:
      overflow_px = x + self.width(string) - WIDTH
      overflow_ch = overflow_px // FONT_WIDTH + 1
      string = string[:-overflow_ch]
    if string == '':
      raise ValueError("trying to draw text off screen")
    return x, string

  def fbtext(self, buffer):
    x, string = self.clip_x()
    y = self.y

    # Build a buffer to send to the FPGA
    buffer.append((x >> 4) & 0xFF)
    buffer.append(((x << 4) & 0xF0) | ((y >> 8) & 0x0F))
    buffer.append(y & 0xFF)
    buffer.append(self.col)
    i = len(buffer)
    buffer.append(0)
    for c in string.encode('ASCII'):
      buffer.append(c - 32)
      buffer[i] += 1  # increment the length field
    assert(buffer[i] <= 0xFF)

  def move(self, x, y):
    self.x += x
    self.y += y
    return self

def show(*args):
  # 0 is the address of the frame in the framebuffer in use.
  # See https://streamlogic.io/docs/reify/nodes/#fbgraphics
  # Offset: active display offset in buffer used if double buffering
  list = [obj.vgr2d() for obj in args if hasattr(obj, 'vgr2d')]
  vgr2d.display2d(0, list, WIDTH, HEIGHT)

  def check_collision_y(list):
    if len(list) == 0:
      return
    list = sorted(list, key=lambda obj: obj.y)
    prev = list[0]
    for obj in list[1:]:
      if obj.y < prev.y + FONT_HEIGHT:
        raise ValueError(f'{prev} overlaps with {obj}')
      prev = obj

  def check_collision_xy(list):
    if len(list) == 0:
      return
    sublist = [list[0]]
    prev = list[0]
    for obj in list[1:]:
      if obj.x < prev.x + prev.width(prev.string):
        # Some overlapping, accumulate the row
        sublist.append(obj)
      else:
        # Since the list is sorted, we can stop checking here
        break
      prev = obj
    return check_collision_y(sublist)

  # Text has no wrapper, we implement it locally.
  # See https://streamlogic.io/docs/reify/nodes/#fbtext
  buffer = bytearray(2) # address 0x0000
  list = [obj for obj in args if hasattr(obj, 'fbtext')]
  list = sorted(list, key=lambda obj: obj.y)
  list = sorted(list, key=lambda obj: obj.x)
  check_collision_xy(list)
  for obj in list:
    obj.fbtext(buffer)
  if len(buffer) > 0:
    fpga.write(0x4503, buffer + b'\xFF\xFF\xFF')

display.show = show
display.Text = Text
