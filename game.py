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
import time
import numpy as np

loadPrcFileData('', 'win-size 1280 800')


class MyApp(ShowBase):

    def __init__(self, numObstacles):
        self.collecting = False
        self.calibrating = False
        self.baselineX = 0
        self.baselineY = 0
        self.numObstacles = numObstacles
        self.hoops = []
        self.camX = 0
        self.camZ = -350
        self.camY = 100
        self.camAngle = -10
        self.screenWidth = 0
        self.screenHeight = 0
        self.score = 0
        self.hoopGap = 800
        self.movementThreshold = 0.2
        self.margin = 0.3

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
        self.xmin = 0
        self.ymin = 0
        self.xmax = 0
        self.ymax = 0


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
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(200, 200, 1)
        self.scene.setPos(0, 0, -100)

        self.taskMgr.add(self.getAngle, "GetAngle")

        self.plane = Plane("assets/luft4.gltf")
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

        

        self.taskMgr.add(self.tskListenerPolling, "Poll the connection listener", -39)
        self.taskMgr.add(self.tskReaderPolling, "Poll the connection reader", -40)

        self.mainMenu = MainMenu(self)

    def resetGame(self):
        self.playing = False
        self.score = 0
        self.scoreText.setText(str(self.score))
        self.scoreTextPath.hide()
        self.plane.reset()
        self.taskMgr.remove("checkHoops")
        self.taskMgr.remove("movePlane")
        self.taskMgr.remove("animateHoops")
        self.mainMenu.mainMenuScreen.show()


    def startGame(self):
        self.generateObstacles()
        self.taskMgr.add(self.checkHoops, "checkHoops")
        self.taskMgr.add(self.movePlane, "movePlane")
        self.taskMgr.add(self.animateHoops, "animateHoops")
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



    def extractBaselines(self):
        if len(self.baselineXarray) !=0 and len(self.baselineYarray) !=0:
            print(self.baselineXarray)
            self.xmin = np.min(self.baselineXarray)
            self.xmax = np.max(self.baselineXarray)
            self.ymin = np.min(self.baselineYarray)
            self.ymax = np.max(self.baselineYarray)
            print(self.xmin,self.xmax,self.ymin,self.ymax)

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
                self.incoming(datagram)

        return Task.cont

    def incoming(self, datagram):

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

        if self.calibrating:
            self.baselineXarray.append(pressurex)
            self.baselineYarray.append(pressurey)
        print(pressurex,pressurey)

        if abs(pressurex) >= self.margin:
            if pressurex < 0:
                #print("moving left")

                self.plane.stopMovingRight()
                self.plane.moveLeft(pressurex)
            else:
                #print("moving right")
                self.plane.stopMovingLeft()
                self.plane.moveRight(pressurex)

        if abs(pressurey) >= self.margin:
            if pressurey < 0:
                #print("moving down")
                self.plane.stopMovingUp()
                self.plane.moveDown(pressurey)
            else:
                #print("moving up")
                self.plane.stopMovingDown()
                self.plane.moveUp(pressurey)

        if abs(pressurex) < self.margin and abs(pressurey) < self.margin:
            self.plane.stopMovingUp()
            self.plane.stopMovingDown()
            self.plane.stopMovingLeft()
            self.plane.stopMovingRight()



    def checkHoops(self, task):
        # get hoop Z and compare to plane Z
        # print(self.hoops[0].getPos()[1], self.plane.actor.getPos()[1])
        if self.hoops[0].getPos()[1] < self.plane.actor.getPos()[1]:
            if len(self.hoops) == 1:
                self.resetGame()
            self.hoops.pop(0).delete()
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


            camCoords = base.camera.getPos()
            base.camera.setPos(camCoords[0], planePos[1] + self.camZ, camCoords[2]) #+ self.camY
        return Task.cont

    def generateObstacles(self):
        for i in range(self.numObstacles):
            hoop = Actor("assets/target.gltf")
            hoop.setScale(50, 50, 50)
            hoop.setPos(random.randint(self.plane.leftLimit, self.plane.rightLimit), -700 + (i * self.hoopGap), random.randint(self.plane.downLimit, self.plane.upLimit))
            hoop.setHpr(0, 90, 0)
            # hoop.setColor(1,0,0,1)
            hoop.reparentTo(self.render)
            self.hoops.append(hoop)

            colliderNode2 = CollisionNode('hoopCollider')
            colliderNode2.addSolid(CollisionCapsule(0, 0, 0, 0, 0, 0.1, 1))
            hoopCollider = hoop.attachNewNode(colliderNode2)
            hoopCollider.setPythonTag("hoop", hoop)
            # hoopCollider.show()

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
