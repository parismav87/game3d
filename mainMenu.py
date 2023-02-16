from direct.gui.DirectGui import *


class MainMenu():
	def __init__(self, game):
		self.game = game
		self.mainMenuScreen = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7), fadeScreen = 0.4, relief = DGG.FLAT)
		# game.font = loader.loadFont("assets/SuperMario256.ttf")
		label = DirectLabel(text = "Flight", parent = self.mainMenuScreen, scale = 0.1, pos = (0, 0, 0.2), text_font = game.font)
		self.calibrateBtn = DirectButton(text = "Calibrate", command = game.calibrate, pos = (0, 0, 0), parent = self.mainMenuScreen, scale = 0.07, pad=(0.1,0.1), text_font = game.font)
		self.baselines = DirectLabel(text = "x: 123 y: 123", parent = self.mainMenuScreen, scale = 0.05, pos = (0, 0, -0.05))
		self.centerBtn = DirectButton(text = "Center", command = game.center, pos = (0, 0, -0.2), parent = self.mainMenuScreen, scale = 0.07, pad=(0.1,0.1), text_font = game.font)
		self.playBtn = DirectButton(text = "Play", command = game.startGame, pos = (0, 0, -0.4), parent = self.mainMenuScreen, scale = 0.07, pad=(0.1,0.1), text_font = game.font)

		self.copBtn = DirectCheckButton(text = "COP", command = self.setCOP, pos = (-0.05, 0, -0.6), parent = self.mainMenuScreen, scale = 0.04, pad=(0.1,0.1), text_font = game.font, indicatorValue = 0)
		self.yprBtn = DirectCheckButton(text = "YPR", command = self.setYPR, pos = (0.1, 0, -0.6), parent = self.mainMenuScreen, scale = 0.04, pad=(0.1,0.1), text_font = game.font, indicatorValue = 1 )
		self.baselines.hide()
		self.mainMenuScreen.show()

	def setCOP(self, status):
		if status:
			self.yprBtn['indicatorValue'] = 0
			self.yprBtn.setIndicatorValue()
			self.game.useYPR = False
		else:
			self.yprBtn['indicatorValue'] = 1
			self.yprBtn.setIndicatorValue()
			self.game.useYPR = True

	def setYPR(self, status):
		if status:
			self.copBtn['indicatorValue'] = 0
			self.copBtn.setIndicatorValue()
			self.game.useYPR = True
		else:
			self.copBtn['indicatorValue'] = 1
			self.copBtn.setIndicatorValue()
			self.game.useYPR = False
