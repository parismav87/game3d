from poseEstimator import *
from game import *
import time
from direct.stdpy import threading
import copyreg, copy, pickle
from multiprocessing import Value


def runGame(game, angle, ready):
    game.initialize(angle, ready)
    game.go()

if __name__ == '__main__':
    try:

        angle = Value('f', 0.0)
        ready = Value('b', 0)

        numObstacles = 100 #[20,100,500]
        complexity = 0 #[0,1,2]
        imshow = False #[True, False]

        game = MyApp(numObstacles)

        # pe = PoseEstimator(imshow, complexity)
        # x = threading.Thread(target = pe.run, args = (angle, ready))
        # x.start()        
        
        
        
        y = threading.Thread(target = game.go(angle, ready)) # , args = (game, angle, ready)
        y.start()

        # x.join()
        y.join()

    except KeyboardInterrupt:
        print("keyboard interrupt!")
  