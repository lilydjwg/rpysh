#!/usr/bin/env python3
# vim:fileencoding=utf-8

import sys
import os
import code
import socket
import pickle
import rlcompleter
import threading
from functools import partial

from rpylib import *

default_port = 8980

def remoteInput(sock, sock2, prompt=''):
  print('fetch remote cmd...', file=sys.__stdout__)
  prompt = prompt.encode()
  sendSizedStr(sock2, prompt)
  t = sock.recv(1)
  if t == IN_INT:
    raise KeyboardInterrupt
  elif t == IN_DATA:
    return sock.recv(1024).decode()
  elif t == IN_BLANKLINE:
    return ''
  else:
    raise EOFError

class Completer(threading.Thread):
  def __init__(self, sock, local):
    self.sock = sock
    self.local = local
    super().__init__()

  def run(self):
    sock = self.sock
    comp = rlcompleter.Completer(self.local)
    try:
      while True:
        pargs = getSizedStr(sock)
        args = pickle.loads(pargs)
        ret = comp.complete(*args)
        sendSizedStr(sock, pickle.dumps(ret))
    except IOError:
      pass

class WritableSockIO:
  def __init__(self, sock):
    self.sock = sock

  def write(self, data):
    self.sock.send(data.encode())

def interact(host, port, banner=None, local=None):
  sock = socket.socket()
  sock.bind((host, port))
  sock.listen(1)
  sock2 = socket.socket()
  sock2.bind((host, port+1))
  sock2.listen(1)

  while True:
    s, a = sock.accept()
    print(a, 'connected.')
    s2, a = sock2.accept()

    try:
      sys.stdout = sys.stderr = WritableSockIO(s)

      console = code.InteractiveConsole(local)
      console.raw_input = partial(remoteInput, s, s2)
      Completer(s2, console.locals).start()
      print('all setup.', file=sys.__stdout__)
      console.interact(banner)

      s.close()
      s2.close()
    finally:
      sys.stdout = sys.__stdout__
      sys.stderr = sys.__stderr__

def usage():
    sys.exit('usage:  %s [port]\n\tport is %d by default' % (os.path.split(sys.argv[0])[1], default_port))

if __name__ == '__main__':
  if len(sys.argv) == 2:
    try:
      port = int(sys.argv[1])
    except ValueError:
      usage()
  elif len(sys.argv) == 1:
    port = default_port
  else:
    usage()

  interact('', port)
