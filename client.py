import socket, pickle

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 5001        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    myfile = open('sin.txt', mode='r')
    for line in myfile.readlines():
        s.sendall(bytes(line, 'utf-8'))
    s.sendall(b'')
    data = s.recv(1024)
print('Received', repr(data))