import socket
import time
from threading import Thread
import matplotlib.pyplot as plt
from quatlib import Quaternion
from numpy.linalg import norm
import numpy as np
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection
from panda3d.core import NetAddress
from panda3d.core import NetDatagram
import time
import pandas as pd
import warnings
import math



class MARG:

    def __init__(self):

        self.quaternion = Quaternion(1, 0, 0, 0)
        self.samplePeriod = 1 / 511.4
        self.beta = 0


    def update(self, gyroscope, accelerometer, magnetometer):
        """
        Perform one update step with data from a AHRS sensor array
        :param gyroscope: A three-element array containing the gyroscope data in radians per second.
        :param accelerometer: A three-element array containing the accelerometer data. Can be any unit since a normalized value is used.
        :param magnetometer: A three-element array containing the magnetometer data. Can be any unit since a normalized value is used.
        :return:
        """
        q = self.quaternion
        gyroscope = np.array(gyroscope, dtype=float).flatten()
        accelerometer = np.array(accelerometer, dtype=float).flatten()
        magnetometer = np.array(magnetometer, dtype=float).flatten()

        # Normalise accelerometer measurement
        if norm(accelerometer) is 0:
            warnings.warn("accelerometer is zero")
            return
        accelerometer /= norm(accelerometer)

        # Normalise magnetometer measurement
        if norm(magnetometer) is 0:
            warnings.warn("magnetometer is zero")
            return
        magnetometer /= norm(magnetometer)

        h = q * (Quaternion(0, magnetometer[0], magnetometer[1], magnetometer[2]) * q.conj())
        b = np.array([0, norm(h[1:3]), 0, h[3]])

        # Gradient descent algorithm corrective step
        f = np.array([
            2 * (q[1] * q[3] - q[0] * q[2]) - accelerometer[0],
            2 * (q[0] * q[1] + q[2] * q[3]) - accelerometer[1],
            2 * (0.5 - q[1] ** 2 - q[2] ** 2) - accelerometer[2],
            2 * b[1] * (0.5 - q[2] ** 2 - q[3] ** 2) + 2 * b[3] * (q[1] * q[3] - q[0] * q[2]) - magnetometer[0],
            2 * b[1] * (q[1] * q[2] - q[0] * q[3]) + 2 * b[3] * (q[0] * q[1] + q[2] * q[3]) - magnetometer[1],
            2 * b[1] * (q[0] * q[2] + q[1] * q[3]) + 2 * b[3] * (0.5 - q[1] ** 2 - q[2] ** 2) - magnetometer[2]
        ])
        j = np.array([
            [-2 * q[2], 2 * q[3], -2 * q[0], 2 * q[1]],
            [2 * q[1], 2 * q[0], 2 * q[3], 2 * q[2]],
            [0, -4 * q[1], -4 * q[2], 0],
            [-2 * b[3] * q[2], 2 * b[3] * q[3], -4 * b[1] * q[2] - 2 * b[3] * q[0], -4 * b[1] * q[3] + 2 * b[3] * q[1]],
            [-2 * b[1] * q[3] + 2 * b[3] * q[1], 2 * b[1] * q[2] + 2 * b[3] * q[0], 2 * b[1] * q[1] + 2 * b[3] * q[3],
             -2 * b[1] * q[0] + 2 * b[3] * q[2]],
            [2 * b[1] * q[2], 2 * b[1] * q[3] - 4 * b[3] * q[1], 2 * b[1] * q[0] - 4 * b[3] * q[2], 2 * b[1] * q[1]]
        ])

        step = j.T @ (f)
        step /= norm(step)  # normalise step magnitude

        # Compute rate of change of quaternion
        qdot = (q * Quaternion(0, gyroscope[0], gyroscope[1], gyroscope[2])) * 0.5 - self.beta * step.T

        # Integrate to yield quaternion
        q += qdot * self.samplePeriod
        self.quaternion = Quaternion(q / norm(q))  # normalise quaternion
        return self.quaternion


def q_to_ypr(q):
    if q:
        yaw = (math.atan2(2 * q[1] * q[2] - 2 * q[0] * q[3], 2 * q[0] ** 2 + 2 * q[1] ** 2 - 1))
        roll = (-1 * math.asin(2 * q[1] * q[3] + 2 * q[0] * q[2]))
        pitch = (math.atan2(2 * q[2] * q[3] - 2 * q[0] * q[1], 2 * q[0] ** 2 + 2 * q[3] ** 2 - 1))
        return [yaw, pitch, roll]

record = MARG()
""" Socket = 1235 

Tο format των πακέτων είναι όμοιο με αυτό των COP, δηλαδή:

"START " + περιεχόμενο + " END"

όπου "περιεχόμενο" = πολλές γραμμές με split character "tab"
όπου η κάθε γραμμή έχει data με split το "space"
όπου η 1η γραμμή είναι general info, όπως "ώρα υπολογιστή" "αριθμός μετρήσεων/followup lines"
και κάθε επόμενη γραμμή να είναι μια μέτρηση με data: "device 1 ή 2", "imu internal counter for measurements",  accx, accy, accz, gyrx, gyry, gyrz, magx, magy, magz"""

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
Hz=10
#writer = pd.ExcelWriter('Timestamps.xlsx')
#text_file = open("data_test.txt", "w")
def SocketListener():
    global socketBuffer
    global timestamp
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', 1235))

                s.listen()
                currenttime=time.time()

                while True:

                    conn, addr = s.accept()

                    with conn:
                        while True:
                            data = conn.recv(100000)
                            #print(data)
                            if len(data) != 0:
                                socketBuffer += data.decode('utf-16')
                                #currenttime2=time.time()
                                #timestamp.append(currenttime2-currenttime)
                                #currenttime=currenttime2



                            else: break
        except: pass
threadSocket = Thread(target = SocketListener)
threadSocket.start()
yaw_list = []
pitch_list = []
roll_list = []
raw_gx = []
raw_gy = []
raw_gz = []
raw_ax = []
raw_ay = []
raw_az = []
raw_mx = []
raw_my = []
raw_mz = []
ypr = []
testing_timestamp=[]
static = pd.read_csv(r'static2.txt', delimiter='\\t', decimal=',')
check_buffer = 0
check_buffer2 = 0
step = 0
try:
    print('READY')
    while True:
        package_array = socketBuffer.split('ENDSTART')



        if len(package_array) > 1:
            socketBuffer = package_array[-1]
            for i in range(len(package_array)-1):
                last_pkg = package_array[i]
                #print(last_pkg)


                if ('START' in last_pkg):
                    last_pkg=last_pkg.replace('START','')
                #if 'END' in last_pkg:
                #last_pkg = last_pkg[:-4]
                lines = last_pkg.split('\t')
                info = lines[0]
                lines = lines[1:]
                #print(info)



                if len(lines)>2:
                    for l in lines:
                        data=l.split(' ')
                        if data[0]=='2':
                            data = data[2:]
                            check_buffer += 1

                            acc = np.array([float(data[0]), float(data[1]), float(data[2])])
                            gyro = np.array([math.radians(float(data[3])-static['Gyro2X'].mean()), math.radians(float(data[4])-static['Gyro2Y'].mean()), math.radians(float(data[5])-static['Gyro2Z'].mean())])
                            # gyro = np.array([math.radians(float(data[3])), math.radians(float(data[4])), math.radians(float(data[5]))])
                            # print(gyro)
                            mag = np.array([float(data[6]), float(data[7]), float(data[8])])
                            q = record.update(gyroscope=gyro,accelerometer=acc,magnetometer=mag)
                            ypr = q_to_ypr(q)


                            if ypr:
                                check_buffer2 += 1
                                yaw = math.degrees(ypr[0])
                                pitch = math.degrees(ypr[1])
                                roll = math.degrees(ypr[2])
                                yaw_list.append(yaw)
                                pitch_list.append(pitch)
                                roll_list.append(roll)
                                step += 1
                                if step == 22:
                                    pkg = NetDatagram()
                                    pkg.addString(str(yaw) + ';' + str(pitch) + ';' + str(roll))
                                    cWriter.send(pkg, myConnection)
                                    #print(str(yaw) + ';' + str(pitch) + ';' + str(roll))
                                    step = 0
                                raw_gx.append((gyro[0]))
                                raw_gy.append((gyro[1]))
                                raw_gz.append((gyro[2]))
                                raw_ax.append((acc[0]))
                                raw_ay.append((acc[1]))
                                raw_az.append((acc[2]))
                                raw_mx.append((mag[0]))
                                raw_my.append((mag[1]))
                                raw_mz.append((mag[2]))

                        else:
                            pass
            #time.sleep(1/5)

except KeyboardInterrupt:
    print('Manually stopped')
    print(check_buffer)
    print(check_buffer2)
    print(len(yaw_list))


    df = pd.DataFrame(
        {'yaw': yaw_list, 'pitch': pitch_list, 'roll': roll_list, 'Gyro1X': raw_gx, 'Gyro1Y': raw_gy, 'Gyro1Z': raw_gz,
         'Acc1X': raw_ax,
         'Acc1Y': raw_ay, 'Acc1Z': raw_az, 'Mag1X': raw_mx, 'Mag1Y': raw_my, 'Mag1Z': raw_mz})
    df.to_csv('velocities.csv')
    fig, (ax,ax2) = plt.subplots(2)
    ax.plot(raw_gx,label='raw_gx')
    ax.plot(raw_gy, label='raw_gy')
    ax.plot(raw_gz, label='raw_gz')
    ax.legend()

    #timestamp_df = pd.DataFrame({'Timestamp 16-12':testing_timestamp})
    #timestamp_df.to_csv('Timestamp at 16-12.csv')
    ax2.plot(yaw_list,label='yaw')
    ax2.plot(pitch_list, label='pitch')
    ax2.plot(roll_list, label='roll')
    ax2.legend()
    plt.show()






