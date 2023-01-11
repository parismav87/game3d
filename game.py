from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Thread, DirectionalLight, AmbientLight, loadPrcFileData, CollisionNode, CollisionCapsule, \
    CollisionSphere, CollisionTraverser, CollisionHandlerEvent, CollisionHandlerQueue, CollisionHandlerPusher, TextNode
from plane import *
import random
from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionListener
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from panda3d.core import PointerToConnection
from panda3d.core import NetAddress
from panda3d.core import NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
import datetime
from direct.gui.DirectGui import *
from mainMenu import *
from settingsMenu import *
import time
import numpy as np
import csv

loadPrcFileData('', 'win-size 1280 800')


class MyApp(ShowBase):

    def __init__(self, numObstacles):
        self.collecting = False
        self.calibrating = False
        self.centering = False
        self.baselineX = 0
        self.baselineY = 0
        self.numObstacles = numObstacles
        self.hoops = []
        self.clouds = []
        self.camX = 0
        self.camZ = -350
        self.camY = 100
        self.camAngle = -10
        self.screenWidth = 0
        self.screenHeight = 0
        self.score = 0
        self.hoopGap = 800
        self.movementThreshold = 0.4
        #self.margin = 0.3

        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.activeConnections = []
        self.port_address = 5000  # No-other TCP/IP services are using this port
        self.backlog = 1000  # If we ignore 1,000 connection attempts, something is wrong!
        self.tcpSocket = self.cManager.openTCPServerRendezvous(self.port_address, self.backlog)
        self.cListener.addConnection(self.tcpSocket)
        self.playing = False
        self.baselineXarray = []
        self.baselineYarray = []
        self.centerXarray = []
        self.centerYarray = []
        self.xmin = 0
        self.ymin = 0
        self.xmax = 0
        self.ymax = 0
        self.centerX = 0
        self.centerY = 0

        self.pressurex = 0
        self.pressurey = 0

        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.yawMin = 0
        self.yawMax = 0
        self.pitchMin = 0
        self.pitchMax = 0
        self.rollMin = 0
        self.rollMax = 0
        self.yawBaseline = []
        self.pitchBaseline = []
        self.rollBaseline = []

        self.balanceYaw = 0
        self.balancePitch = 0
        self.balanceRoll = 0

        self.centerYawarray = []
        self.centerPitcharray = []

        self.currentYaw_angle = 0
        self.currentPitch_angle = 0
        self.currentRoll_angle = 0


    def initialize(self, angle, ready):

        ShowBase.__init__(self)
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.pusher.add_in_pattern("%fn-into-%in")

        self.font = self.loader.loadFont("assets/SuperMario256.ttf")

        dlight = AmbientLight('dlight')
        dlnp = render.attachNewNode(dlight)
        render.setLight(dlnp)

        self.screenWidth = base.win.getProperties().getXSize()
        self.screenHeight = base.win.getProperties().getYSize()

        self.angle = angle
        self.scoreText = TextNode('scoreText')
        self.scoreText.setFont(self.font)
        self.scoreText.setText(str(self.score))
        self.scoreTextPath = aspect2d.attachNewNode(self.scoreText)
        self.scoreTextPath.setScale(0.15)
        self.scoreTextPath.setPos(1, 0, 0.8)
        self.scoreTextPath.hide()

        self.outputCSV = open('movement.csv', 'w', newline= '')
        self.csvWriter = csv.writer(self.outputCSV, delimiter=',')
        self.csvWriter.writerow(['planeX,planeY,planeZ,targetX,targetY,targetZ,pressureX,pressureY'])

        # self.calibrationText = TextNode('calibrationText')
        # self.calibrationText.setText("Calibrating...")
        # self.calibrationTextPath = aspect2d.attachNewNode(self.calibrationText)
        # self.calibrationTextPath.setScale(0.1)
        # self.calibrationText.setFont(self.font)
        # self.calibrationTextPath.setPos(-0.4, 0, 0.1)
        # self.calibrationTextPath.hide()

        # self.countdownText = TextNode('countdownText')
        # self.countdownText.setText('10')
        # self.countdownTextPath = aspect2d.attachNewNode(self.countdownText)
        # self.countdownTextPath.setScale(0.1)
        # self.countdownText.setFont(self.font)
        # self.countdownTextPath.setPos(-0.15, 0, 0.3)
        # self.countdownTextPath.hide()

        base.setBackgroundColor(r=136 / 255, g=210 / 255, b=235 / 255)
        # self.scene = self.loader.loadModel("models/environment")
        # self.scene.reparentTo(self.render)
        # self.scene.setScale(200, 200, 1)
        # self.scene.setPos(0, 0, -100)

        

        self.taskMgr.add(self.getAngle, "GetAngle")

        self.plane = Plane("assets/luft6.gltf")
        self.plane.actor.reparentTo(self.render)
        planePos = self.plane.actor.getPos()

        base.disableMouse()
        base.camera.setPos(0, planePos[1] + self.camZ, planePos[2] + self.camY)
        base.camera.setHpr(0, self.camAngle, 0)

        
        # self.taskMgr.add(self.moveObstacles, "moveObstacles")

        colliderNode = CollisionNode('planeCollider')
        sphere = CollisionSphere(0, 0, 0, 7)
        sphere.setTangible(False)
        colliderNode.addSolid(sphere)
        planeCollider = self.plane.actor.attachNewNode(colliderNode)
        planeCollider.setPythonTag("planeC", self.plane)
        # planeCollider.show()

        base.pusher.addCollider(planeCollider, self.plane.actor)
        base.cTrav.addCollider(planeCollider, self.pusher)

        self.accept("planeCollider-into-hoopCollider", self.handleCollision)

        self.settingsBtn = DirectButton(text = "Settings", command = self.openSettings, pos = (-1.4,0,0.9), scale = 0.04, pad=(0.1,0.1))

        self.taskMgr.add(self.tskListenerPolling, "Poll the connection listener", -39)
        self.taskMgr.add(self.tskReaderPolling, "Poll the connection reader", -40)

        self.mainMenu = MainMenu(self)
        self.settingsMenu = SettingsMenu(self)

    def openSettings(self):
        self.settingsMenu.settingsMenuScreen.show()

    def resetGame(self):
        self.playing = False
        self.score = 0
        self.scoreText.setText(str(self.score))
        self.scoreTextPath.hide()
        self.plane.reset()
        self.taskMgr.remove("checkHoops")
        self.taskMgr.remove("movePlane")
        # self.taskMgr.remove("animateHoops")
        self.mainMenu.mainMenuScreen.show()


    def startGame(self):
        self.generateObstacles()
        self.generateClouds()
        self.taskMgr.add(self.checkHoops, "checkHoops")
        self.taskMgr.add(self.movePlane, "movePlane")
        # self.taskMgr.add(self.animateHoops, "animateHoops")
        self.mainMenu.mainMenuScreen.hide()
        self.scoreTextPath.show()
        self.playing = True

    def calibrate(self):
        if not self.calibrating:
            self.calibrating = True
            self.mainMenu.calibrateBtn.setText("Stop")
        else:
            self.calibrating = False
            self.mainMenu.calibrateBtn.setText("Calibrate")
            self.extractBaselines()

    def center(self):
        if not self.centering:
            self.centering = True
            self.mainMenu.centerBtn.setText("Stop")
        else:
            self.centering = False
            self.mainMenu.centerBtn.setText("Center")
            self.extractCenter()

    def extractCenter(self):
        if len(self.centerXarray) !=0 and len(self.centerYarray) !=0:
            self.centerX = np.mean(self.centerXarray)
            self.centerY = np.mean(self.centerYarray)
            print(self.centerX, self.centerY)

            if len(self.baselineXarray)!=0: #normalize if range exists
                self.centerX = 2 * (self.centerX - self.xmin) / (self.xmax - self.xmin) - 1  # normalize to [-1, 1]
                self.centerY = 2 * (self.centerY - self.ymin) / (self.ymax - self.ymin) - 1  # normalize to [-1, 1]

        self.balanceYaw = 0
        self.balancePitch = 0
        self.balanceRoll = 0

    def extractBaselines(self):

        if len(self.yawBaseline)!=0 and len(self.pitchBaseline)!=0 and len(self.rollBaseline)!=0:


            self.yawMin = np.min(self.yawBaseline)
            self.yawMax = np.max(self.yawBaseline)
            self.pitchMin = np.min(self.pitchBaseline)
            self.pitchMax = np.max(self.pitchBaseline)
            self.rollMin = np.min(self.rollBaseline)
            self.rollMax = np.max(self.rollBaseline)
            print('limits ', ' yawMin: ',self.yawMin,' yawMax: ' ,self.yawMax,' rollMin: ', self.rollMin,' rollMax: ', self.rollMax)


            # self.balanceYaw = 2 * (self.balanceYaw - self.yawMin) / (self.yawMax - self.yawMin) - 1
            # self.balancePitch = 2 * (self.balancePitch - self.pitchMin) / (self.pitchMax - self.pitchMin) - 1
            # self.balanceRoll = 2 * (self.balanceRoll - self.rollMin) / (self.rollMax - self.rollMin) - 1

            self.balanceYaw = 0
            self.balancePitch = 0
            self.balanceRoll = 0

        if len(self.baselineXarray) !=0 and len(self.baselineYarray) !=0:
            print(self.baselineXarray)
            self.xmin = np.min(self.baselineXarray)
            self.xmax = np.max(self.baselineXarray)
            self.ymin = np.min(self.baselineYarray)
            self.ymax = np.max(self.baselineYarray)



            if len(self.centerXarray) != 0: # normalize centers if centers exist
                self.centerX = 2 * (self.centerX - self.xmin) / (self.xmax - self.xmin) - 1  # normalize to [-1, 1]
                self.centerY = 2 * (self.centerY - self.ymin) / (self.ymax - self.ymin) - 1  # normalize to [-1, 1]

    def tskListenerPolling(self, taskdata):
        if self.cListener.newConnectionAvailable():
            print("new connection! ")

            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.activeConnections.append(newConnection)  # Remember connection
                self.cReader.addConnection(newConnection)  # Begin reading connection
        return Task.cont

    def tskReaderPolling(self, taskdata):
        if self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                # print("get data")
                # print(datagram)
                # self.incomingCOP(datagram)
                self.incomingYPR(datagram)

        return Task.cont

    def incomingYPR(self, datagram):
        iterator = PyDatagramIterator(datagram)
        yprString = iterator.getString().replace(",", ".")
        yprList = yprString.split(";")
        #print(yprList)

        yaw = float(yprList[0]) # x
        pitch = float(yprList[1])
        roll = float(yprList[2]) # y

        #print(yaw, pitch, roll)

        self.currentRoll_angle = roll
        self.currentPitch_angle = pitch
        self.currentYaw_angle = yaw

        if self.playing:
            yaw = 2 * (self.currentYaw_angle - self.yawMin) / (self.yawMax - self.yawMin) - 1  # normalize to [-1, 1]
            pitch = 2 * (self.currentPitch_angle - self.pitchMin) / (self.pitchMax - self.pitchMin) - 1  # normalize to [-1, 1]
            roll = 2 * (self.currentRoll_angle - self.rollMin) / (self.rollMax - self.rollMin) - 1  # normalize to [-1, 1]

        #print(self.currentYaw_angle, self.currentPitch_angle, self.currentRoll_angle)

        # if not self.collecting:
        #     self.collecting = True
        #     self.baselineX = pressurex
        #     self.baselineY = pressurey
        # print(pressurex, pressurey)

        self.yaw = yaw
        self.pitch = pitch
        self.roll = -roll



        if self.calibrating:
            self.yawBaseline.append(self.currentYaw_angle)
            self.pitchBaseline.append(self.currentPitch_angle)
            self.rollBaseline.append(self.currentRoll_angle)
        # print(pressurex,pressurey)

        if self.centering:
            self.centerYawarray.append(self.yaw)
            self.centerPitcharray.append(self.roll)
        #print(pressurex, pressurey)

        if abs(self.yaw) >= self.balanceYaw + self.movementThreshold:
            if self.yaw < self.balanceYaw:
                #print("moving left")

                self.plane.stopMovingRight()
                self.plane.moveLeft(self.yaw/2)
            else:
                #print("moving right")
                self.plane.stopMovingLeft()
                self.plane.moveRight(self.yaw/2)

        if abs(self.roll) >= self.balanceRoll + self.movementThreshold:
            if self.roll < self.balanceRoll:
                #print("moving down")
                self.plane.stopMovingUp()
                self.plane.moveDown(self.roll/2)
            else:
                #print("moving up")
                self.plane.stopMovingDown()
                self.plane.moveUp(self.roll/2)

        if abs(self.yaw) < self.balanceYaw + self.movementThreshold and abs(self.roll) < self.balanceRoll + self.movementThreshold: # balanced (no move)
            self.plane.stopMovingUp()
            self.plane.stopMovingDown()
            self.plane.stopMovingLeft()
            self.plane.stopMovingRight()






    def incomingCOP(self, datagram):

        # print(datagram)

        iterator = PyDatagramIterator(datagram)
        pressure = iterator.getString().replace(",", ".")
        # print(pressure)
        xy = pressure.split(";")
        # print(pressure)

        # xy = re.sub(r'[^\x00-\x7F]+','-', xy)
        pressurex = float(xy[0])
        pressurey = float(xy[1])


        # xy[0][i] xy[0][i-1]
        if self.playing:
            pressurex = 2 * (float(xy[0]) - self.xmin) / (self.xmax - self.xmin) - 1  # normalize to [-1, 1]
            pressurey = 2 * (float(xy[1]) - self.ymin) / (self.ymax - self.ymin) - 1  # normalize to [-1, 1]

        # if not self.collecting:
        #     self.collecting = True
        #     self.baselineX = pressurex
        #     self.baselineY = pressurey
        # print(pressurex, pressurey)

        self.pressurey = pressurey
        self.pressurex = pressurex

        if self.calibrating:
            self.baselineXarray.append(pressurex)
            self.baselineYarray.append(pressurey)
        # print(pressurex,pressurey)

        if self.centering:
            self.centerXarray.append(pressurex)
            self.centerYarray.append(pressurey)
        # print(pressurex, pressurey)

        if abs(pressurex) >= self.centerX + self.movementThreshold:
            if pressurex < self.centerX:
                #print("moving left")

                self.plane.stopMovingRight()
                self.plane.moveLeft(pressurex)
            else:
                #print("moving right")
                self.plane.stopMovingLeft()
                self.plane.moveRight(pressurex)

        if abs(pressurey) >= self.centerY + self.movementThreshold:
            if pressurey < self.centerY:
                #print("moving down")
                self.plane.stopMovingUp()
                self.plane.moveDown(pressurey)
            else:
                #print("moving up")
                self.plane.stopMovingDown()
                self.plane.moveUp(pressurey)

        if abs(pressurex) < self.centerX + self.movementThreshold and abs(pressurey) < self.centerY + self.movementThreshold: # balanced (no move)
            self.plane.stopMovingUp()
            self.plane.stopMovingDown()
            self.plane.stopMovingLeft()
            self.plane.stopMovingRight()



    def checkHoops(self, task):
        # get hoop Z and compare to plane Z
        # print(self.hoops[0].getPos()[1], self.plane.actor.getPos()[1])
        # print(self.hoops[0].getAncestors()[0].isHidden())
        if self.hoops[0].getPos()[1] < self.plane.actor.getPos()[1]:
            if len(self.hoops) == 1:
                self.resetGame()
            self.hoops.pop(0).delete()
        self.hoops[0].show() #getAncestors()[1].showThrough()
        return Task.cont

    def animateHoops(self, task):
        hpr = self.hoops[0].getHpr()
        for hoop in self.hoops:
            hoop.setHpr(hpr[0], hpr[1], hpr[2])
        return Task.cont

    def handleCollision(self, entry):

        self.score += 1
        self.scoreText.setText(str(self.score))
        collider = entry.getIntoNodePath()
        hoop = collider.getPythonTag("hoop")
        collider.clearPythonTag("hoop")
        hoop.delete()
        self.hoops.pop(0)
        if len(self.hoops) == 0:
            self.resetGame()

    def movePlane(self, task):

        if self.playing:

            planePos = self.plane.actor.getPos()
            planeHpr = self.plane.actor.getHpr()
            # print(planeHpr[2])
            # print(planePos[2])

            newX = planePos[0] - self.plane.leftMove + self.plane.rightMove
            if newX > self.plane.rightLimit:
                newX = self.plane.rightLimit
            elif newX < self.plane.leftLimit:
                newX = self.plane.leftLimit

            newY = planePos[2] - self.plane.downMove + self.plane.upMove
            if newY > self.plane.upLimit:
                newY = self.plane.upLimit
            elif newY < self.plane.downLimit:
                newY = self.plane.downLimit

            # print(newX, newY)

            self.plane.actor.setPos(newX, planePos[1] + self.plane.speed, newY)

            if self.plane.leftMove != 0 or self.plane.rightMove != 0:
                self.plane.rotatePlaneHorizontal(planeHpr)
            else:
                self.plane.recoverRotationHorizontal(planeHpr)

            planeHpr = self.plane.actor.getHpr()

            if self.plane.upMove != 0 or self.plane.downMove != 0:
                self.plane.rotatePlaneVertical(planeHpr)
            else:
                self.plane.recoverRotationVertical(planeHpr)

            currentPos = self.plane.actor.getPos()
            firstObstacle = self.hoops[0].getPos()
            row = [str(currentPos[0]) + ',' + str(currentPos[2]) + ',' + str(currentPos[1]) + ',' + str(firstObstacle[0]) + ',' + str(firstObstacle[2]) + ',' + str(firstObstacle[1]) + ',' + str(self.pressurex) + ',' + str(self.pressurey)]
            self.csvWriter.writerow(row)

            camCoords = base.camera.getPos()
            base.camera.setPos(camCoords[0], planePos[1] + self.camZ, camCoords[2]) #+ self.camY
        return Task.cont

    def generateObstacles(self):
        for i in range(self.numObstacles):
            hoop = Actor("assets/target2.gltf")
            hoop.setScale(50, 50, 50)
            hoop.setPos(random.randint(self.plane.leftLimit, self.plane.rightLimit), -700 + (i * self.hoopGap), random.randint(self.plane.downLimit, self.plane.upLimit))
            # hoop.setHpr(0, 0, 0)
            # hoop.setColor(1,0,0,1)
            hoop.reparentTo(self.render)
            self.hoops.append(hoop)

            

            colliderNode2 = CollisionNode('hoopCollider')
            colliderNode2.addSolid(CollisionCapsule(0, 0, 0, 0, 0, 0.1, 1))
            hoopCollider = hoop.attachNewNode(colliderNode2)
            hoopCollider.setPythonTag("hoop", hoop)
            # hoopCollider.show()
            if i>0: #hide all except 1st target
                hoop.hide()

    def generateClouds(self):
        for i in range(self.numObstacles//2):
            cloud = Actor("assets/cloud.gltf")
            cloud.reparentTo(self.render)
            cloud.setPos(random.randint(self.plane.leftLimit-3000, self.plane.rightLimit+3000), -700 + (i * self.hoopGap*2), random.randint(self.plane.downLimit-300, self.plane.downLimit))
            cloud.setScale(100, 100, 100)
            self.clouds.append(cloud)


    def getAngle(self, task):
        # print(self.angle.value)
        if self.angle.value > 0:
            self.plane.setPos(self.plane, 1, 0, 0)
        elif self.angle.value < 0:
            self.plane.setPos(self.plane, -1, 0, 0)
        return Task.cont

    def go(self, angle, ready):
        self.initialize(angle, ready)
        self.run()
