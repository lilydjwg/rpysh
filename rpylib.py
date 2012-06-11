import struct

INT_SIZE = struct.calcsize('!I')
IN_DATA = b'\x00'
IN_INT = b'\x01'
IN_BLANKLINE = b'\x02'

def getSizedStr(sock):
  blen = sock.recv(INT_SIZE)
  l = struct.unpack('!I', blen)[0]
  got = 0
  ret = b''
  while got < l:
    ret += sock.recv(l-got)
    got += len(ret)
  return ret

def sendSizedStr(sock, s):
  p = struct.pack('!I', len(s))
  p += s
  sock.send(p)
