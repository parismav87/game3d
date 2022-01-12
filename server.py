import socket
import sys

class Server():
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 5001
        sock.bind(('localhost', port))
        
        

    def run(self, angle, ready):
        sock.listen(1)
        while True:
            try: 
                conn, info = sock.accept()
                data = conn.recv(1024)
                while data:
                    print(data)
            except KeyboardInterrupt:
                conn.close()

