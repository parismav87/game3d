from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection
from panda3d.core import NetAddress
from panda3d.core import NetDatagram
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np

def minMaxNormalisation(arr):
    maxx = np.amax(arr)
    minn = np.amin(arr)
    minmax = []
    for k,v in enumerate(arr):
        minmax.append((v-minn)/(maxx - minn))

    return minmax

def stringToFloat(arr):
    result = []
    for v in arr:
        f = float(v.replace(",", "."))
        result.append(f)
    return result



cManager = QueuedConnectionManager()
cReader = QueuedConnectionReader(cManager, 0)
cWriter = ConnectionWriter(cManager, 0)
activeConnections = []
port_address = 5000 #No-other TCP/IP services are using this port
ip_address = '127.0.0.1'
timeout = 3000
myConnection = cManager.openTCPClientConnection(ip_address, port_address, timeout)

df = pd.read_csv('swing.txt', sep='\t')
df= df[1:]
weightLeft = df['WeightA'].tolist()
weightRight = df['WeightB'].tolist()

weightLeft = stringToFloat(weightLeft)
weightRight = stringToFloat(weightRight)

weightLeft = minMaxNormalisation(weightLeft)
weightRight = minMaxNormalisation(weightRight)

# plt.plot(weightLeft)
# plt.plot(weightRight)
# plt.show()

# print(weightLeft)
# print(weightRight)


if myConnection:
    cReader.addConnection(myConnection)
    print("connected!")
    for k,v in enumerate(weightLeft):
        pkg = NetDatagram()
        coords = str(v) + ':' + str(weightRight[k])
        pkg.addString(coords)
        cWriter.send(pkg, myConnection)
        time.sleep(0.01)

