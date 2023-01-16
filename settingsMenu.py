from direct.gui.DirectGui import *


class SettingsMenu():
	def __init__(self, game):
		self.game = game
		self.settingsMenuScreen = DirectDialog(frameSize = (-1.5, -1, 0.6, -0.6), fadeScreen = 0.4, relief = DGG.FLAT)
		label = DirectLabel(text = "Settings", parent = self.settingsMenuScreen, scale = 0.06, pos = (-1.25, 0, 0.5))

		thresholdLabel = DirectLabel(text = "Balance threshold", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, 0.4))
		self.thresholdSlider = DirectSlider(range=(0,0.5), value=0.25, pageSize=3, command=self.setThreshold, pos = (-1.25, 0, 0.35), scale = 0.2 , parent = self.settingsMenuScreen)
		self.thresholdValue = label = DirectLabel(text = "0.25", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, 0.3))

		speedLabel = DirectLabel(text = "Speed", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, 0.2))
		self.speedSlider = DirectSlider(range=(0,5), value=2.5, pageSize=3, command=self.setSpeed, pos = (-1.25, 0, 0.15), scale = 0.2 , parent = self.settingsMenuScreen)
		self.speedValue = DirectLabel(text = "2.5", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, 0.1))

		planeScaleLabel = DirectLabel(text = "Plane size", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, 0.0))
		self.planeScaleSlider = DirectSlider(range=(1,9), value=5, pageSize=3, command=self.setPlaneScale, pos = (-1.25, 0, -0.05), scale = 0.2 , parent = self.settingsMenuScreen)
		self.planeScaleValue = DirectLabel(text = "5", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, -0.1))

		hoopScaleLabel = DirectLabel(text = "Target size", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, -0.2))
		self.hoopScaleSlider = DirectSlider(range=(1,9), value=5, pageSize=3, command=self.setHoopScale, pos = (-1.25, 0, -0.25), scale = 0.2 , parent = self.settingsMenuScreen)
		self.hoopScaleValue = DirectLabel(text = "5", parent = self.settingsMenuScreen, scale = 0.04, pos = (-1.25, 0, -0.3))


		self.resetBtn = DirectButton(text = "Reset", parent=self.settingsMenuScreen, command = self.resetGame, pos = (-1.25,0,-0.45), scale = 0.03, pad=(0.1,0.1))

		self.closeBtn = DirectButton(text = "Close", parent=self.settingsMenuScreen, command = self.settingsMenuScreen.hide, pos = (-1.25,0,-0.55), scale = 0.03, pad=(0.1,0.1))
		self.settingsMenuScreen.hide()

	def setThreshold(self):
		thresh = round(self.thresholdSlider['value'],2)
		self.thresholdValue.setText(str(thresh))
		self.game.movementThreshold = thresh

	def setSpeed(self):
		speed = round(self.speedSlider['value'],2)
		self.speedValue.setText(str(speed))
		self.game.plane.speed = speed

	def setPlaneScale(self):
		planeScale = round(self.planeScaleSlider['value'])
		self.planeScaleValue.setText(str(planeScale))
		self.game.plane.actor.setScale(planeScale,planeScale,planeScale)

	def setHoopScale(self):
		hoopScale = round(self.hoopScaleSlider['value'])
		self.hoopScaleValue.setText(str(hoopScale))
		for hoop in self.game.hoops:
			hoop.setScale(10*hoopScale, 10*hoopScale, 10*hoopScale)

	def resetGame(self):
		self.game.resetGame()
		self.settingsMenuScreen.hide()
