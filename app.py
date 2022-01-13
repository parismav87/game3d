from poseEstimator import *
from game import *
import time
from direct.stdpy import threading
import copyreg, copy, pickle
from multiprocessing import Value
import asyncio
import socketio

if __name__ == '__main__':
    try:

        angle = Value('f', 0.0)
        ready = Value('b', 0)

        numObstacles = 10 #[20,100,500]
        complexity = 0 #[0,1,2]
        imshow = False #[True, False]

        game = MyApp(numObstacles)
        # client = Client()

        # pe = PoseEstimator(imshow, complexity)
        # x = threading.Thread(target = client.run(angle, ready))
        # x.start()       


        y = threading.Thread(target = game.go(angle, ready)) # , args = (game, angle, ready)
        y.start()

        # x.join()
        y.join()
        

    except KeyboardInterrupt:
        print("keyboard interrupt!")
  