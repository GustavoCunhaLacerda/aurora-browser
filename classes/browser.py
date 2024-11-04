import tkinter
import tkinter.font

from classes.url import URL
from classes.text import Text
from classes.tag import Tag
from classes.layout import Layout

# Constantes para dimensões da interface e espaçamento do texto
WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18  # Espaço horizontal e vertical entre caracteres
SCROLL_STEP = 100  # Tamanho do passo para ação de rolagem
SCROLL_W = 15
SCROLL_H = 40
SCROLL_COLOR = "#2c3e50"

class Browser:
  """Um navegador usando Tkinter para renderizar conteúdo WEB."""
  
  def __init__(self):
    """Inicializa a janela principal, o canvas e configura os eventos de rolagem e redimensionamento."""
    self.h = HEIGHT
    self.w = WIDTH
    self.scroll = 0 # Posição inicial de rolagem
    
    # Configura a janela principal e o canvas
    self.window = tkinter.Tk()
    self.window.title("Aurora Browser")
    
    # Canvas para exibir o conteúdo
    self.canvas = tkinter.Canvas(self.window, width=self.w, height=self.h)
    self.canvas.pack(fill="both", expand=True)
    
    # Associa eventos de rolagem e redimensionamento
    self.window.bind("<Down>", self.scrolldown)
    self.window.bind("<Up>", self.scrollup)
    self.window.bind("<MouseWheel>", self.scrollmouse)
    self.canvas.bind("<Configure>", self.resize)
    
  def load(self, url: URL):
    """Carrega e exibe o conteúdo da URL especificada."""
    url.request()
    body = url.response["content"]
    self.tokens = self.lex(body)
    self.display_list = Layout(self.tokens, self.w - SCROLL_W).display_list
    self.max_scroll = self.calculate_max_scroll()
    self.draw()
  
  def lex(self, body):
    """Remove as tags HTML para retornar apenas o texto puro."""
    out = []
    buffer = ""
    in_tag = False
    
    for c in body:
      if c == "<":
        in_tag = True
        if buffer: out.append(Text(buffer))
        buffer = ""
      elif c == ">":
        in_tag = False
        if buffer: out.append(Tag(buffer))
        buffer = ""
      else:
        buffer += c
    
    if not in_tag and buffer:
      out.append(Text(buffer))
    return out
  
  def draw(self):
    """Desenha o conteúdo de texto no canvas com base no layout e na posição de rolagem."""
    self.canvas.delete("all")
    
    for x, y, c, f in self.display_list:
      if y - self.scroll > self.h: continue
      if y + VSTEP < self.scroll: continue
      self.canvas.create_text(x, y - self.scroll, text=c, anchor='nw', font=f)
      
    self.draw_scrollbar()
      
  def scrolldown(self, e):
    """Rola o conteúdo para baixo e redesenha."""
    self.scroll = min(self.scroll + SCROLL_STEP, self.max_scroll)
    self.draw()
    
  def scrollup(self, e):
    """Rola o conteúdo para cima e redesenha."""
    self.scroll = max(0, self.scroll - SCROLL_STEP)
    self.draw()
  
  def scrollmouse(self, e):
    """Rola o conteúdo usando a roda do mouse."""
    if e.delta > 0:
      self.scrollup(e)
    else:
      self.scrolldown(e)
  
  def resize(self, e):
    """Atualiza as dimensões do canvas ao redimensionar a janela e redesenha o conteúdo."""
    self.w = e.width
    self.h = e.height
    
    self.display_list = Layout(self.tokens, self.w - SCROLL_W).display_list
    self.max_scroll = self.calculate_max_scroll()
    self.draw()
    
    
  def draw_scrollbar(self):
    """Desenha a barra de rolagem no lado direito do canvas."""
    percentage = self.scroll / max(self.max_scroll, 1)
    y_value = min(percentage * self.h, self.h - SCROLL_H)
    
    self.canvas.create_rectangle(self.w - SCROLL_W, 0 + y_value, self.w, SCROLL_H + y_value, fill=SCROLL_COLOR, outline=SCROLL_COLOR)
    self.canvas.create_line(self.w - SCROLL_W, 0, self.w - SCROLL_W, self.h, fill=SCROLL_COLOR)
  
  def calculate_max_scroll(self):
    """Calcula a rolagem máxima com base na altura do conteúdo."""
    last_y = self.display_list[-1][1]
    return max(0, last_y - self.h + VSTEP)