import socket
import ssl
from typing import List, Tuple

class URL:
  def __init__(self, url: str):
    """Inicializa a URL e configura o esquema específico (http, https, file)."""
    self.scheme, url = url.split("://", 1)
    
    if self.scheme not in ["http", "https", "file"]:
      raise ValueError("Scheme not supported.")
    
    if self.scheme == "file":
      self.path = url
    if self.scheme in ["http", "https"]:
        self.host, self.path, self.port = self.parse_http_url(url)

  def parse_http_url(self, url: str):
    """Analisa a URL HTTP/HTTPS e retorna host, caminho e porta."""
    port = 443 if self.scheme == "https" else 80
    if "/" not in url:
      url = url + "/"

    host, url = url.split("/", 1)
    path = "/" + url

    if ":" in host:
      host, port = host.split(":", 1)
      port = int(port)
      
    return host, path, port
      
  def request(self):
    """Realiza a requisição HTTP ou lê um arquivo local."""
    try:
        if self.scheme in ["http", "https"]:
            self.do_http_request()
        elif self.scheme == "file":
            self.do_file_request()
    except Exception as e:
        print(f"Error during request: {e}")
      
  
  def do_http_request(self):
    """Configura e envia uma requisição HTTP/HTTPS e armazena a resposta."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP) as s:
      if self.scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=self.host)
      s.connect((self.host, self.port))
      
      request = self.build_request_headers([
        ("Host", self.host),
        ("Connection", "Close")
      ])

      s.send(request)
      self.response = self.read_response(s)
  
  def do_file_request(self):
    """Lê o conteúdo de um arquivo local."""
    try:
      with open(self.path, "r") as file:
        content = file.read()
        self.response = { "content": content }
    except FileNotFoundError:
      self.response = { "content": f"File not found: {self.path}" }
  
  def build_request_headers(self, headers: List[Tuple[str, str]], httpVersion: str = "1.1") -> bytes:
    """Constrói o cabeçalho da requisição HTTP."""
    request = f"GET {self.path} HTTP/{httpVersion}\r\n"
    for header in headers:
      name, value = header
      request += f"{name}: {value}\r\n"
    request += "\r\n"

    return request.encode("utf8")

  def read_response(self, s: socket):
    """Lê a resposta da requisição HTTP."""
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

  def show_content(self):
    """Exibe o conteúdo da resposta (limitado para visualização)."""
    isInTag = False
    
    for character in self.response["content"]:
      if character == "<":
        isInTag = True
      elif character == ">":
        isInTag = False
      elif not isInTag:
        print(character, end="")


def load(url: URL):
  """Carrega a URL e exibe o conteúdo."""
  url.request()
  url.show_content()

if __name__ == "__main__":
  import sys
  if len(sys.argv) > 1:
    try:
        load(URL(sys.argv[1]))
    except Exception as e:
        print(f"Error: {e}")
  else:
    print("Please provide a URL as an argument.")
