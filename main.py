import socket
import ssl
from typing import List, Tuple

class URL:
  def __init__(self, url: str):
    self.scheme, url = url.split("://", 1)
    assert self.scheme in ["http", "https", "file"]
    
    if(self.scheme in ["http", "https"]):
      self.bootHttpUrlConfigs(url)
    elif(self.scheme in ["file"]):
      self.bootFileConfigs(url)
    
  
  def bootFileConfigs(self, url: str):
    self.path = url
    
  def bootHttpUrlConfigs(self, url: str):
    if self.scheme == "http":
      self.port = 80
    elif self.scheme == "https":
      self.port = 443

    if "/" not in url:
      url = url + "/"

    self.host, url = url.split("/", 1)
    self.path = "/" + url

    if ":" in self.host:
      self.host, port = self.host.split(":", 1)
      self.port = int(port)
      
  def request(self):
    if(self.scheme in ["http", "https"]):
      self.doHttpRequest()
    elif(self.scheme in ["file"]):
      self.doFileRequest()
      
  
  def doHttpRequest(self):
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)

    if self.scheme == "https":
      ctx = ssl.create_default_context()
      s = ctx.wrap_socket(s, server_hostname=self.host)

    s.connect((self.host, self.port))
    
    request = self.buildRequestHeaders([
      ("Host", self.host),
      ("Connection", "Close")
    ])

    s.send(request)
    response = self.readResponse(s)
    s.close()

    self.response = response
  
  def doFileRequest(self):
    with open(self.path, "r") as file:
        content = file.read()
        self.response = {
          "content": content
        }
  
  def buildRequestHeaders(self, headers: List[Tuple[str, str]], httpVersion: str = "1.1") -> bytes:
    request = f"GET {self.path} HTTP/{httpVersion}\r\n"
    for header in headers:
      name, value = header
      request += f"{name}: {value}\r\n"
    request += "\r\n"

    return request.encode("utf8")

  def readResponse(self, s: socket):
    response = s.makefile("r", encoding="utf8", newline="\r\n")
    
    statusLine = response.readline()
    version, status, explanation = statusLine.split(" ", 2)

    responseHeaders = {}
    while True:
      hLine = response.readline()
      if hLine == "\r\n": break
      header, value = hLine.split(":", 1)
      responseHeaders[header.casefold()] = value.strip()

    content = response.read()

    return {
      "version": version,
      "status": status,
      "explanation": explanation,
      "headers": responseHeaders,
      "content": content
    }

  def showContent(self):
    isInTag = False
    print(self.response)
    for character in self.response["content"]:
      if character == "<":
        isInTag = True
      elif character == ">":
        isInTag = False
      elif not isInTag:
        print(character, end="")


def load(url: URL):
  url.request()
  url.showContent()

if __name__ == "__main__":
  import sys
  load(URL(sys.argv[1]))
