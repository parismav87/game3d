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
import math

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

def q_to_ypr(q):
    if q:
        yaw = (math.atan2(2 * q[1] * q[2] - 2 * q[0] * q[3], 2 * q[0] ** 2 + 2 * q[1] ** 2 - 1))
        roll = (-1 * math.asin(2 * q[1] * q[3] + 2 * q[0] * q[2]))
        pitch = (math.atan2(2 * q[2] * q[3] - 2 * q[0] * q[1], 2 * q[0] ** 2 + 2 * q[3] ** 2 - 1))
        return [yaw, pitch, roll]




cManager = QueuedConnectionManager()
cReader = QueuedConnectionReader(cManager, 0)
cWriter = ConnectionWriter(cManager, 0)
activeConnections = []
port_address = 5000 #No-other TCP/IP services are using this port
ip_address = '127.0.0.1'
timeout = 3000
myConnection = cManager.openTCPClientConnection(ip_address, port_address, timeout)

df = pd.read_csv('quat.csv', sep=',')
df= df[1:]
# print(df)
w = df['w'].tolist()
x = df['x'].tolist()
y = df['y'].tolist()
z = df['z'].tolist()

# print(df)
# weightLeft = df['WeightA'].tolist()
# weightRight = df['WeightB'].tolist()

# w = stringToFloat(w)
# x = stringToFloat(x)
# y = stringToFloat(y)
# z = stringToFloat(z)

# weightLeft = minMaxNormalisation(weightLeft)
# weightRight = minMaxNormalisation(weightRight)

# plt.plot(weightLeft)
# plt.plot(weightRight)
# plt.show()

# print(weightLeft)
# print(weightRight)


if myConnection:
    cReader.addConnection(myConnection)
    print("connected!")
    for k,v in enumerate(w):
        pkg = NetDatagram()
        ypr = q_to_ypr([w[k], x[k], y[k], z[k]])
        coords = str(ypr[0]) + ";" + str(ypr[1]) + ";" + str(ypr[2]) 
        pkg.addString(coords)
        cWriter.send(pkg, myConnection)
        time.sleep(0.01)

