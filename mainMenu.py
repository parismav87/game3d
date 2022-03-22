from direct.gui.DirectGui import *



class MainMenu():
	def __init__(self, game):
		self.mainMenuScreen = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7), fadeScreen = 0.4, relief = DGG.FLAT)
		# game.font = loader.loadFont("assets/SuperMario256.ttf")
		label = DirectLabel(text = "Flight", parent = self.mainMenuScreen, scale = 0.1, pos = (0, 0, 0.2), text_font = game.font)
		self.calibrateBtn = DirectButton(text = "Calibrate", command = game.calibrate, pos = (0, 0, 0), parent = self.mainMenuScreen, scale = 0.07, pad=(0.1,0.1), text_font = game.font)
		self.playBtn = DirectButton(text = "Play", command = game.startGame, pos = (0, 0, -0.2), parent = self.mainMenuScreen, scale = 0.07, pad=(0.1,0.1), text_font = game.font)
		self.mainMenuScreen.show()
