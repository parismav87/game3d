from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Thread, loadPrcFileData, CollisionNode, CollisionCapsule, CollisionSphere, CollisionTraverser, CollisionHandlerEvent, CollisionHandlerQueue


class Plane():

    def __init__(self, model):

        self.actor = Actor(model)
        self.speed = 2
        self.acceleration = 2
        self.rotationAcceleration = 2
        self.rotationSpeed = 2
        self.rotationRecovery = 2
        self.turnSpeed = 0.2
        self.turnSpeedLimit = 10
        self.rotationSpeedLimit = 15
        self.leftMove = 0
        self.rightMove = 0
        self.upMove = 0
        self.downMove = 0
        self.xAngle = 0
        self.yAngle = 0
        self.zAngle = 0
        self.rightLimit = 140
        self.leftLimit = -140
        self.upLimit = 200
        self.downLimit = 50


        self.actor.setScale(5,5,5)
        self.actor.setPos(0, -1000, 100)
        self.actor.setHpr(self.xAngle, self.yAngle, self.zAngle)

        self.actor.accept("arrow_left", self.moveLeft, [-1])
        self.actor.accept("arrow_left-repeat", self.moveLeft, [-1])
        self.actor.accept("arrow_left-up", self.stopMovingLeft)

        self.actor.accept("arrow_right", self.moveRight, [1])
        self.actor.accept("arrow_right-repeat", self.moveRight, [1])
        self.actor.accept("arrow_right-up", self.stopMovingRight)

        self.actor.accept("arrow_up", self.moveUp, [1])
        self.actor.accept("arrow_up-repeat", self.moveUp, [1])
        self.actor.accept("arrow_up-up", self.stopMovingUp)

        self.actor.accept("arrow_down", self.moveDown, [-1])
        self.actor.accept("arrow_down-repeat", self.moveDown, [-1])
        self.actor.accept("arrow_down-up", self.stopMovingDown)

    def reset(self):
        self.actor.setPos(0, -1000, 100)
        self.actor.setHpr(self.xAngle, self.yAngle, self.zAngle)

    def recoverRotationHorizontal(self, planeHpr):
        horizontalRotation = planeHpr[2]
        newHorizontal = self.xAngle

        if horizontalRotation>self.xAngle: #recover horizontal
            if horizontalRotation > self.xAngle + self.rotationRecovery:
                newHorizontal = horizontalRotation - self.rotationRecovery
        elif horizontalRotation < self.xAngle:
            if horizontalRotation < self.xAngle - self.rotationRecovery:
                newHorizontal = horizontalRotation + self.rotationRecovery


        
        self.actor.setHpr(planeHpr[0], planeHpr[1], newHorizontal)



    def recoverRotationVertical(self, planeHpr):
        verticalRotation = planeHpr[1]
        newVertical = self.yAngle

        if verticalRotation > self.yAngle: #recover vertical
            if verticalRotation > self.yAngle + self.rotationRecovery:
                newVertical = verticalRotation - self.rotationRecovery

        elif verticalRotation < self.yAngle:
            if verticalRotation < self.yAngle - self.rotationRecovery:
                newVertical = verticalRotation + self.rotationRecovery

        
        self.actor.setHpr(planeHpr[0], newVertical, planeHpr[2])


    def rotatePlaneHorizontal(self, planeHpr):
        # print(planeHpr[0])
        rotationHorizontal = planeHpr[2] - self.rotationSpeed*self.leftMove + self.rotationSpeed*self.rightMove

        if rotationHorizontal > self.xAngle + self.rotationSpeedLimit:
            rotationHorizontal = self.xAngle + self.rotationSpeedLimit
        elif rotationHorizontal < self.xAngle - self.rotationSpeedLimit:
            rotationHorizontal = self.xAngle - self.rotationSpeedLimit

        self.actor.setHpr(planeHpr[0], planeHpr[1], rotationHorizontal) 

        
    def rotatePlaneVertical(self, planeHpr):
        rotationVertical = planeHpr[1] - self.rotationSpeed*self.downMove + self.rotationSpeed*self.upMove

        if rotationVertical > self.yAngle + self.rotationSpeedLimit:
            rotationVertical = self.yAngle + self.rotationSpeedLimit
        elif rotationVertical < self.yAngle - self.rotationSpeedLimit:
            rotationVertical = self.yAngle - self.rotationSpeedLimit 

        self.actor.setHpr(planeHpr[0], rotationVertical, planeHpr[2]) 


    def moveLeft(self,speed):
        speed = abs(speed)

        self.leftMove += 1*speed*self.turnSpeed
        if self.leftMove > self.turnSpeedLimit:
            self.leftMove = self.turnSpeedLimit


    def stopMovingLeft(self):
        self.leftMove = 0

    def moveRight(self,speed):
        speed = abs(speed)
        self.rightMove += 1*speed*self.turnSpeed
        if self.rightMove > self.turnSpeedLimit:
            self.rightMove = self.turnSpeedLimit

    def stopMovingRight(self):
        self.rightMove = 0

    def moveUp(self,speed):
        speed = abs(speed)
        self.upMove +=  1*speed*self.turnSpeed
        if self.upMove > self.turnSpeedLimit:
            self.upMove = self.turnSpeedLimit

    def stopMovingUp(self):
        self.upMove = 0

    def moveDown(self,speed):
        speed = abs(speed)
        self.downMove += 1*speed*self.turnSpeed
        if self.downMove > self.turnSpeedLimit:
            self.downMove = self.turnSpeedLimit

    def stopMovingDown(self):
        self.downMove = 0
