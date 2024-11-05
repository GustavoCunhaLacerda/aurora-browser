class Element:
  def __init__(self, tag, parent):
    self.tag = tag
    self.children = []
    self.parent = parent