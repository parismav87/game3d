from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Thread, DirectionalLight, AmbientLight, loadPrcFileData, CollisionNode, CollisionCapsule, CollisionSphere, CollisionTraverser, CollisionHandlerEvent, CollisionHandlerQueue, CollisionHandlerPusher, TextNode
from plane import *
import random

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

        if newX < -self.screenWidth/2:
            newX = -self.screenWidth/2
        elif newX > self.screenWidth/2:
            newX = self.screenWidth/2

        if newY < -self.screenHeight/2:
            newY = -self.screenHeight/2
        elif newY > self.screenHeight/2:
            newY = self.screenHeight/2

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

