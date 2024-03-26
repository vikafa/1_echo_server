import socket
from time import sleep

port=int(input("port:"))
sock = socket.socket()
sock.setblocking(1)
sock.connect(('localhost', port))

msg = input("Your string:")
#msg = "Hi!"
sock.send(msg.encode())

data = sock.recv(1024)

sock.close()

print(data.decode())
