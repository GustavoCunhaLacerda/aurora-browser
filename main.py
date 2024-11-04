import tkinter

from classes.browser import Browser
from classes.url import URL

if __name__ == "__main__":
  import sys
  Browser().load(URL(sys.argv[1]))
  tkinter.mainloop()