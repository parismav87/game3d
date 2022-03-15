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
                s.bind(('localhost', 1234))

                s.listen()
                currenttime=time.time()

                while True:

                    conn, addr = s.accept()

                    with conn:
                        while True:
                            data = conn.recv(1024)
                            #print(data)
                            if len(data) != 0:
                                socketBuffer += data.decode('utf-16')
                                currenttime2=time.time()
                                timestamp.append(currenttime2-currenttime)
                                currenttime=currenttime2
                                #print((socketBuffer))


                            else: break
        except: pass
threadSocket = Thread(target = SocketListener)
threadSocket.start()

while True:

    last_pkg = socketBuffer.split('ENDSTART')[-1]

    if ('START' in last_pkg):
        last_pkg=last_pkg.replace('START','')

    #last_pkg.replace('END','')
    print(last_pkg)

    if 'END' in last_pkg:
        print(last_pkg)
        CoPX = last_pkg.split()[1]

        CoPY = last_pkg.split()[2]



        print(CoPX, CoPY)


        pkg = NetDatagram()
        pkg.addString(CoPX+';'+CoPY)

        cWriter.send(pkg, myConnection)
        time.sleep(1/20)



