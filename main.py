import tkinter

from classes.browser import Browser
from classes.url import URL
from classes.htmlparser import HTMLParser

def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)

if __name__ == "__main__":
  import sys
  url = URL(sys.argv[1])
  # Browser().load(url)
  url.request()
  body = url.response["content"]
  nodes = HTMLParser(body).parse()
  print_tree(nodes)
  tkinter.mainloop()
