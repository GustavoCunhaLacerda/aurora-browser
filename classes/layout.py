import tkinter

from classes.text import Text

HSTEP, VSTEP = 13, 18
FONTS = {}

class Layout:
  def __init__(self, tokens, effective_width):
    self.cursor_x = HSTEP
    self.cursor_y = VSTEP
    self.effective_width = effective_width
    
    self.weight = "normal"
    self.style = "roman"
    self.size = 12
    
    self.display_list = []
    self.line = []
    
    for token in tokens:
      self.token(token)
    self.flush()
      
  def token(self, token):
    if isinstance(token, Text):
      for word in token.text.split():
        self.word(word)

    elif token.tag == "i":
      self.style = "italic"
    elif token.tag == "/i":
      self.style = "roman"
    elif token.tag == "b":
      self.weight = "bold"
    elif token.tag == "/b":
      self.weight = "normal"
    elif token.tag == "small":
      self.size -= 2
    elif token.tag == "/small":
      self.size += 2
    elif token.tag == "big":
      self.size += 4
    elif token.tag == "/big":
      self.size -= 4
    elif token.tag == "br":
      self.flush()
    elif token.tag == "/p":
      self.flush()
      self.cursor_y += VSTEP
    elif token.tag == "/p":
      self.flush()
      self.cursor_y += VSTEP
    elif token.tag == "/h1" or token.tag == "/title":
      self.flush()
      self.cursor_y += VSTEP
      
  def word(self, word):
    font = self.get_font(self.size, self.weight, self.style)
    word_size = font.measure(word)
    font_space_size = font.measure(" ")
    
    # Avança para a próxima linha se o texto atingir a largura do canvas
    if self.cursor_x + word_size > self.effective_width:
      self.flush()
    
    self.line.append((self.cursor_x, word, font))
    self.cursor_x += word_size + font_space_size
    
  def flush(self):
    if not self.line: return
    metrics = [font.metrics() for x, word, font in self.line]
    max_ascent = max([metric["ascent"] for metric in metrics])
    
    baseline = self.cursor_y + 1.25 * max_ascent
    
    for x, word, font in self.line:
      y = baseline - font.metrics("ascent")
      self.display_list.append((x, y, word, font))
    
    max_descent = max([metric["descent"] for metric in metrics])
    self.cursor_y = baseline + 1.25 * max_descent
    
    self.cursor_x = HSTEP
    self.line = []
  
  def get_font(self, size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
      font = tkinter.font.Font(size=size, weight=weight, slant=style)
      label = tkinter.Label(font=font) # Recomendação da doc para melhorar o desempenho do font.metrics
      FONTS[key] = (font, label)
    return FONTS[key][0]
