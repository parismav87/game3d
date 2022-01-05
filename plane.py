from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Thread, loadPrcFileData, CollisionNode, CollisionCapsule, CollisionSphere, CollisionTraverser, CollisionHandlerEvent, CollisionHandlerQueue


class Plane():

    def __init__(self, model):

        self.actor = Actor(model)
        self.speed = 2
        self.rotationSpeed = 1
        self.rotationRecovery = 2
        self.turnSpeed = 1
        self.turnSpeedLimit = 2
        self.rotationSpeedLimit = 45
        self.leftMove = 0
        self.rightMove = 0
        self.upMove = 0
        self.downMove = 0

        self.actor.setScale(5,5,5)
        self.actor.setPos(0, -1000, 100)

        self.actor.accept("arrow_left", self.moveLeft)
        self.actor.accept("arrow_left-repeat", self.moveLeft)
        self.actor.accept("arrow_left-up", self.stopMovingLeft)

        self.actor.accept("arrow_right", self.moveRight)
        self.actor.accept("arrow_right-repeat", self.moveRight)
        self.actor.accept("arrow_right-up", self.stopMovingRight)

        self.actor.accept("arrow_up", self.moveUp)
        self.actor.accept("arrow_up-repeat", self.moveUp)
        self.actor.accept("arrow_up-up", self.stopMovingUp)

        self.actor.accept("arrow_down", self.moveDown)
        self.actor.accept("arrow_down-repeat", self.moveDown)
        self.actor.accept("arrow_down-up", self.stopMovingDown)


    def recoverRotationHorizontal(self, planeHpr):
        horizontalRotation = planeHpr[2]
        newHorizontal = 0

        if horizontalRotation>0: #recover horizontal
            if horizontalRotation > self.rotationRecovery:
                newHorizontal = horizontalRotation - self.rotationRecovery
        elif horizontalRotation < 0:
            if horizontalRotation < -self.rotationRecovery:
                newHorizontal = horizontalRotation + self.rotationRecovery


        
        self.actor.setHpr(planeHpr[0], planeHpr[1], newHorizontal)



    def recoverRotationVertical(self, planeHpr):
        verticalRotation = planeHpr[1]
        newVertical = 0

        if verticalRotation > 0: #recover vertical
            if verticalRotation > self.rotationRecovery:
                newVertical = verticalRotation - self.rotationRecovery
        elif verticalRotation < 0:
            if verticalRotation < - self.rotationRecovery:
                newVertical = verticalRotation + self.rotationRecovery

        
        self.actor.setHpr(planeHpr[0], newVertical, planeHpr[2])


    def rotatePlaneHorizontal(self, planeHpr):
        rotationHorizontal = planeHpr[2]-self.rotationSpeed*self.leftMove+self.rotationSpeed*self.rightMove

        if rotationHorizontal > self.rotationSpeedLimit:
            rotationHorizontal = self.rotationSpeedLimit
        elif rotationHorizontal < -self.rotationSpeedLimit:
            rotationHorizontal = -self.rotationSpeedLimit

        self.actor.setHpr(planeHpr[0], planeHpr[1], rotationHorizontal) 

        
    def rotatePlaneVertical(self, planeHpr):
        rotationVertical = planeHpr[1]-self.rotationSpeed*self.downMove+self.rotationSpeed*self.upMove

        if rotationVertical > self.rotationSpeedLimit:
            rotationVertical = self.rotationSpeedLimit
        elif rotationVertical < -self.rotationSpeedLimit:
            rotationVertical = -self.rotationSpeedLimit

        self.actor.setHpr(planeHpr[0], rotationVertical, planeHpr[2]) 


    def moveLeft(self):
        self.leftMove = self.turnSpeed

    def stopMovingLeft(self):
        self.leftMove = 0

    def moveRight(self):
        self.rightMove = self.turnSpeed

    def stopMovingRight(self):
        self.rightMove = 0

    def moveUp(self):
        self.upMove = self.turnSpeed

    def stopMovingUp(self):
        self.upMove = 0

    def moveDown(self):
        self.downMove = self.turnSpeed

    def stopMovingDown(self):
        self.downMove = 0
