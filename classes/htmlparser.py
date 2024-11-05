from classes.text import Text
from classes.element import Element

SELF_CLOSING_TAGS = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"]

class HTMLParser:
  def __init__(self, body):
    self.body = body
    self.unfinished = []
    self.SELF_CLOSING_TAGS = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"]
    
  def parse(self):
    text = ""
    in_tag = False
    for c in self.body:
      if c == "<":
          in_tag = True
          if text: self.add_text(text)
          text = ""
      elif c == ">":
          in_tag = False
          print(text)
          self.add_tag(text)
          text = ""
      else:
          text += c
    if not in_tag and text:
      self.add_text(text)
    return self.finish()
  
  def add_text(self, text):
    parent = self.unfinished[-1] if self.unfinished else None
    node = Text(text, parent)
    parent.children.append(node)
  
  def add_tag(self, tag):
    if tag.startswith("!"): return
    if tag.startswith("/"):
      if len(self.unfinished) == 1: return
      node = self.unfinished.pop()
      parent = self.unfinished[-1]
      parent.children.append(node)
    elif tag in self.SELF_CLOSING_TAGS:
      parent = self.unfinished[-1]
      node = Element(tag, parent)
      parent.children.append(node)
    else:
      parent = self.unfinished[-1] if self.unfinished else None
      node = Element(tag, parent)
      self.unfinished.append(node)
  
  def finish(self):
    while len(self.unfinished) > 1:
      node = self.unfinished.pop()
      parent = self.unfinished[-1]
      parent.children.append(node)
    return self.unfinished.pop()