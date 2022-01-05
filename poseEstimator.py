import cv2
import mediapipe as mp
import time
import csv
import math
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

landmarksMapping = {
    0: "nose",
    1: "left_eye_inner",
    2: "left_eye",
    3: "left_eye_outer",
    4: "right_eye_inner",
    5: "right_eye",
    6: "right_eye_outer",
    7: "left_ear",
    8: "right_ear",
    9: "mouth_left",
    10: "mouth_right",
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist", 
    16: "right_wrist",
    17: "left_pinky",
    18: "right_pinky",
    19: "left_index",
    20: "right_index",
    21: "left_thumb",
    22: "right_thumb",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
    29: "left_heel",
    30: "right_heel",
    31: "left_foot_index",
    32: "right_foot_index",
}

font = cv2.FONT_HERSHEY_SIMPLEX
angLeftText = (10,30)
angRightText = (300,30)
fontScale = 0.5
fontColor = (255,0,0)
lineType = 2

data = {}
data[0] = ['timestamp']
for lm in landmarksMapping:
  data[0].append(landmarksMapping[lm]+"_x")
  data[0].append(landmarksMapping[lm]+"_y")
  data[0].append(landmarksMapping[lm]+"_z")
  data[0].append(landmarksMapping[lm]+"_v")
data[0].append("angle_left")
data[0].append("angle_right")





class PoseEstimator:
  
  def __init__(self, imshow, complexity):
    print("created PoseEstimator")
    self.imshow = imshow
    self.complexity = complexity

  def findAngle(self,ax,ay,bx,by,cx,cy): #a = shoulder, b = elbow, c = wrist
    a = math.sqrt((bx-cx)**2 + (by-cy)**2)
    b = math.sqrt((ax-cx)**2 + (ay-cy)**2)
    c = math.sqrt((ax-bx)**2 + (ay-by)**2)
    cosb = (b**2 - a**2 -c**2)/(-2*a*c)
    anglec = round(math.degrees(math.acos(cosb)),2)
    return anglec

  def run(self, angle, ready):

    # outputVideo = cv2.VideoWriter('output.mp4', 0x7634706d, 30.0, (640,480))
    with open('poseCSV.csv', 'w', newline='') as csvFile:
      csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      csvWriter.writerow(data[0])

      # For webcam input:
      cap = cv2.VideoCapture(1)
      # print(cap.get(3), cap.get(4))
      # cap.set(3, 480)
      # cap.set(4, 320)
      start = time.time()
      with mp_pose.Pose(
          min_detection_confidence=0.5,
          min_tracking_confidence=0.5, model_complexity = self.complexity) as pose:
        while cap.isOpened():
          success, image = cap.read()
          ready.value = 1
          if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

          # print("from pose thing: ", angle.value)
          # Flip the image horizontally for a later selfie-view display, and convert
          # the BGR image to RGB.
          image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
          # To improve performance, optionally mark the image as not writeable to
          # pass by reference.
          image.flags.writeable = False
          results = pose.process(image)

          # Draw the pose annotation on the image.
          image.flags.writeable = True
          image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
          mp_drawing.draw_landmarks(
              image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
          now = time.time() - start
          data[now] = [now]
          for k,ld in enumerate(results.pose_landmarks.landmark):
            data[now].append(ld.x)
            data[now].append(ld.y)
            data[now].append(ld.z)
            data[now].append(ld.visibility)
          # print(data[now])

          # angLeft = self.findAngle(data[now][49],data[now][50],data[now][57],data[now][58],data[now][65],data[now][66])
          # angRight = self.findAngle(data[now][45],data[now][46],data[now][53],data[now][54],data[now][61],data[now][62])

          if data[now][66] < data[now][62]: #left wrist above right wrist
            angle.value = 1.0
          elif data[now][66] > data[now][62]: 
            angle.value = -1.0
          else: 
            angle.value = 0

          # data[now].append(angLeft)
          # data[now].append(angRight)
          csvWriter.writerow(data[now])
          
          # cv2.putText(image, "Angle left arm: "+str(angLeft), angLeftText, font, fontScale, fontColor, lineType)
          # cv2.putText(image, "Angle right arm: "+str(angRight), angRightText, font, fontScale, fontColor, lineType)
          if self.imshow:
            cv2.imshow('MediaPipe Pose', image)

          # outputVideo.write(image)

          if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        csvFile.close()
        # outputVideo.release()
        cap.release()
        cv2.destroyAllWindows()

      





