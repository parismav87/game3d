import socket
import time
from threading import Thread
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection
from panda3d.core import NetAddress
from panda3d.core import NetDatagram
import time

cManager = QueuedConnectionManager()
cReader = QueuedConnectionReader(cManager, 0)
cWriter = ConnectionWriter(cManager, 0)
activeConnections = []
port_address = 5000 #No-other TCP/IP services are using this port
ip_address = '127.0.0.1'
timeout = 3000
myConnection = cManager.openTCPClientConnection(ip_address, port_address, timeout)
if myConnection:
    cReader.addConnection(myConnection)


socketBuffer = ''
timestamp=[]
def SocketListener():
    global socketBuffer
    global timestamp
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', 8089))
                s.listen()
                currenttime=time.time()
                while True:
                    conn, addr = s.accept()
                    with conn:
                        while True:
                            data = conn.recv(1024)
                            if len(data) != 0:
                                socketBuffer += data.decode('utf-8')
                                currenttime2=time.time()
                                timestamp.append(currenttime2-currenttime)
                                currenttime=currenttime2
                            else: break
        except: break
threadSocket = Thread(target = SocketListener)
threadSocket.start()
while True:
    if '\t' in socketBuffer:
        tempbuffer=socketBuffer.rsplit('\t',1)
        socketBuffer = tempbuffer[1]
        measurements=tempbuffer[0].split('\t')
        for i in measurements:
            items=i.split(';')
            print(items)
            pkg = NetDatagram()
            pkg.addString(i)
            cWriter.send(pkg, myConnection)
                # data = s.recv(1024)
                # s.close() 