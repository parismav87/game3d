from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Thread, DirectionalLight, AmbientLight, loadPrcFileData, CollisionNode, CollisionCapsule, CollisionSphere, CollisionTraverser, CollisionHandlerEvent, CollisionHandlerQueue, CollisionHandlerPusher, TextNode
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
import re


loadPrcFileData('', 'win-size 1280 800') 


class MyApp(ShowBase):

    def __init__(self, numObstacles):

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

        self.cManager = QueuedConnectionManager()
        self.cListener = QueuedConnectionListener(self.cManager, 0)
        self.cReader = QueuedConnectionReader(self.cManager, 0)
        self.cWriter = ConnectionWriter(self.cManager, 0)
        self.activeConnections = []
        self.port_address = 5000 #No-other TCP/IP services are using this port
        self.backlog = 1000 #If we ignore 1,000 connection attempts, something is wrong!
        self.tcpSocket = self.cManager.openTCPServerRendezvous(self.port_address, self.backlog)
        self.cListener.addConnection(self.tcpSocket)



    def initialize(self, angle, ready):

       
        ShowBase.__init__(self)
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.pusher.add_in_pattern("%fn-into-%in")

        dlight = AmbientLight('dlight')
        dlnp = render.attachNewNode(dlight)
        render.setLight(dlnp)

        
        self.screenWidth = base.win.getProperties().getXSize()
        self.screenHeight = base.win.getProperties().getYSize()

        self.angle = angle
        self.scoreText = TextNode('scoreText')
        self.scoreText.setText(str(self.score))
        self.scoreTextPath = aspect2d.attachNewNode(self.scoreText)
        self.scoreTextPath.setScale(0.07)
        self.scoreTextPath.setPos(1,0,0.9)

        base.setBackgroundColor(r=136/255,g=210/255,b=235/255)
        self.scene = self.loader.loadModel("models/environment")
        self.scene.reparentTo(self.render)
        self.scene.setScale(200,200,1)
        self.scene.setPos(0, 0, -100)

        self.taskMgr.add(self.getAngle, "GetAngle")

        self.plane = Plane("assets/luft.gltf")
        self.plane.actor.reparentTo(self.render)
        planePos = self.plane.actor.getPos()

        base.disableMouse()
        base.camera.setPos(0, planePos[1]+self.camZ, planePos[2]+self.camY)
        base.camera.setHpr(0,self.camAngle,0)

        self.generateObstacles()
        self.taskMgr.add(self.checkHoops, "checkHoops")
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


        self.taskMgr.add(self.movePlane, "movePlane")
        self.taskMgr.add(self.animateHoops, "animateHoops")


        self.taskMgr.add(self.tskListenerPolling, "Poll the connection listener", -39)
        self.taskMgr.add(self.tskReaderPolling, "Poll the connection reader", -40)


    def tskListenerPolling(self, taskdata):
        if self.cListener.newConnectionAvailable():
            print("new connection! ")

            rendezvous = PointerToConnection()
            netAddress = NetAddress()
            newConnection = PointerToConnection()

            if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
                newConnection = newConnection.p()
                self.activeConnections.append(newConnection) # Remember connection
                self.cReader.addConnection(newConnection)     # Begin reading connection
        return Task.cont

    def tskReaderPolling(self, taskdata):
        if self.cReader.dataAvailable():
            datagram = NetDatagram()
            if self.cReader.getData(datagram):
                print("get data")
                print(datagram)
                self.incoming(datagram)

        return Task.cont

    def incoming(self, datagram):
        # print(datagram)
        iterator = PyDatagramIterator(datagram)
        pressure = iterator.getString().replace(",",".")
        xy = pressure.split(";")
        # print(pressure)
        # print(xy)
        # xy = re.sub(r'[^\x00-\x7F]+','-', xy)
        pressurex = float(xy[0])
        pressurey = float(xy[1])
        print(pressurex,pressurey)

        # if pressurex.startswith("-"):
        #     print(pressurex)
        #     print(pressurex[1:])
        #     pressurex = float(pressurex[1:]) * (-1)
        # else:
        #     pressurex = float(pressurex)
        # if pressurey.startswith("-"):
        #     pressurey = float(pressurey[1:]) * (-1)
        # else:
        #     pressurey = float(pressurey)

        print(pressurex, pressurey)
        if pressurex<0:
            print("moving left")
            self.plane.stopMovingRight()
            self.plane.moveLeft()
        else:
            print("moving right")
            self.plane.stopMovingLeft()
            self.plane.moveRight()
        if pressurey<0:
            print("moving down")
            self.plane.stopMovingUp()
            self.plane.moveDown()
        else:
            print("moving up")
            self.plane.stopMovingDown()
            self.plane.moveUp()


    def checkHoops(self, task):
        #get hoop Z and compare to plane Z
        # print(self.hoops[0].getPos()[1], self.plane.actor.getPos()[1])
        if self.hoops[0].getPos()[1] < self.plane.actor.getPos()[1]:
            self.hoops.pop(0).delete()
        return Task.cont

    def animateHoops(self, task):
        hpr = self.hoops[0].getHpr()
        for hoop in self.hoops:
            hoop.setHpr(hpr[0], hpr[1], hpr[2]+1)
        return Task.cont

    def handleCollision(self, entry):
        self.score += 1
        self.scoreText.setText(str(self.score))
        collider = entry.getIntoNodePath()
        hoop = collider.getPythonTag("hoop")
        collider.clearPythonTag("hoop")
        hoop.delete()
        self.hoops.pop(0)
        

    def movePlane(self, task):
        planePos = self.plane.actor.getPos()
        planeHpr = self.plane.actor.getHpr()
        # print(planeHpr[2])
        # print(planePos[0])

        newX = planePos[0] - self.plane.leftMove + self.plane.rightMove
        newY = planePos[2] - self.plane.downMove + self.plane.upMove

        # if newX < -self.screenWidth/2:
        #     newX = -self.screenWidth/2
        # elif newX > self.screenWidth/2:
        #     newX = self.screenWidth/2

        # if newY < -self.screenHeight/2:
        #     newY = -self.screenHeight/2
        # elif newY > self.screenHeight/2:
        #     newY = self.screenHeight/2

        # print(newX, newY)

        self.plane.actor.setPos(newX, planePos[1]+self.plane.speed, newY)

        if self.plane.leftMove !=0 or self.plane.rightMove!=0:
            self.plane.rotatePlaneHorizontal(planeHpr)
        else:
            self.plane.recoverRotationHorizontal(planeHpr)

        planeHpr = self.plane.actor.getHpr()

        if self.plane.upMove!=0 or self.plane.downMove!=0:
            self.plane.rotatePlaneVertical(planeHpr)
        else:
            self.plane.recoverRotationVertical(planeHpr)

        
        base.camera.setPos(planePos[0]+self.camX, planePos[1]+self.camZ, planePos[2]+self.camY)
        return Task.cont


    def generateObstacles(self):
        for i in range(self.numObstacles):
            hoop = Actor("assets/target.gltf")
            hoop.setScale(50,50,50)
            hoop.setPos(random.randint(-300,300),-700+(i*self.hoopGap),random.randint(80, 300))
            # hoop.setHpr(90,0,0)
            # hoop.setColor(1,0,0,1)
            hoop.reparentTo(self.render)
            self.hoops.append(hoop)

            colliderNode2 = CollisionNode('hoopCollider')
            colliderNode2.addSolid(CollisionCapsule(0, 0, 0, 0, 1, 0, 1))
            hoopCollider = hoop.attachNewNode(colliderNode2)
            hoopCollider.setPythonTag("hoop", hoop)
            # hoopCollider.show()

    def getAngle(self, task):
        # print(self.angle.value)
        if self.angle.value > 0:
            self.plane.setPos(self.plane, 1,0,0)
        elif self.angle.value < 0:
            self.plane.setPos(self.plane, -1,0,0)
        return Task.cont

    def go(self, angle, ready):
        self.initialize(angle, ready)
        self.run()

