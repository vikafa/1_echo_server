import socket

port=int(input("port:"))
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', port))
print("Server is starting")
sock.listen(0)
print("Port",port,"is listing")
conn, addr = sock.accept()
print("Client is accepted")
print("Client adress:",addr[0])
print("Client port:",addr[1])

msg = ''

while True:
	data = conn.recv(1024)
	if not data:
            print("All data is accepted")
            break
	msg += data.decode()
	conn.send(msg.upper().encode())

print(msg)

conn.close()
