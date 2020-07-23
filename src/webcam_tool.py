# author: chihiro doi
# creation: 2020-06-23
#
# > python3 webcam_tool.py
# [q] : quit app
# [w] : output current parameters (camera.setting)
# [r] : recording (toggle)

import cv2
from datetime import datetime as dt
import time
import os

DEVICE_ID = 0
FPS=30
#320 240 640 480 800 600
#1280 720
WIDTH=320
HEIGHT=240
#WIDTH=640
#HEIGHT=480

PATH = 'camera.setting'

rec_writer = None

# for pc
#cap = cv2.VideoCapture(DEVICE_ID)
# for jetson
cap = cv2.VideoCapture(DEVICE_ID, cv2.CAP_V4L2)

# cv2.WINDOW_NORMAL
# cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO | cv2.GUI_EXPANDED
cv2.namedWindow("setting", cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO )

# callback , set parameter
def callback_brightness(x):
  cap.set(cv2.CAP_PROP_BRIGHTNESS, x/100)
def callback_contrast(x):
  cap.set(cv2.CAP_PROP_CONTRAST, x/100)
def callback_saturation(x):
  cap.set(cv2.CAP_PROP_SATURATION, x/100)
def callback_hue(x):
  cap.set(cv2.CAP_PROP_HUE, x/100)
def callback_exposure(x):
  cap.set(cv2.CAP_PROP_EXPOSURE, x/100)

# input setting file, get parameter
def input_params(cap, path):
  # load setting file
  if os.path.isfile(PATH):
    with open(PATH) as f:
      lparams = f.readlines()
      #print(lparams)
    for param in lparams:
      param = param.strip()
      keyval = param.split(":")
      if keyval[0] == "CAP_PROP_BRIGHTNESS":
        cap.set(cv2.CAP_PROP_BRIGHTNESS, float(keyval[1]))
      if keyval[0] == "CAP_PROP_CONTRAST":
        cap.set(cv2.CAP_PROP_CONTRAST, float(keyval[1]))
      if keyval[0] == "CAP_PROP_SATURATION":
        cap.set(cv2.CAP_PROP_SATURATION, float(keyval[1]))
      if keyval[0] == "CAP_PROP_HUE":
        cap.set(cv2.CAP_PROP_HUE, float(keyval[1]))
      if keyval[0] == "CAP_PROP_EXPOSURE":
        cap.set(cv2.CAP_PROP_EXPOSURE, float(keyval[1]))

def init(cap):
  # basic setting
  cap.set(cv2.CAP_PROP_FPS, FPS)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
  w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
  h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
  cv2.resizeWindow("setting",int(w),int(h))
  # read setting file
  input_params(cap, PATH)

def update_param(cap):
  cap.set(cv2.CAP_PROP_BRIGHTNESS, cap.get(cv2.CAP_PROP_BRIGHTNESS))
  cap.set(cv2.CAP_PROP_CONTRAST, cap.get(cv2.CAP_PROP_CONTRAST))
  cap.set(cv2.CAP_PROP_SATURATION, cap.get(cv2.CAP_PROP_SATURATION))
  cap.set(cv2.CAP_PROP_HUE, cap.get(cv2.CAP_PROP_HUE))
  cap.set(cv2.CAP_PROP_EXPOSURE, cap.get(cv2.CAP_PROP_EXPOSURE))

def build_trackbar(cap):
  # webcam parameters 
  # https://qiita.com/opto-line/items/7ade854c26a50a485159
  val = int(cap.get(cv2.CAP_PROP_BRIGHTNESS)*100)
  cv2.createTrackbar('CAP_PROP_BRIGHTNESS','setting',val,100, callback_brightness)
  val = int(cap.get(cv2.CAP_PROP_CONTRAST)*100)
  cv2.createTrackbar('CAP_PROP_CONTRAST','setting',val,100, callback_contrast)
  val = int(cap.get(cv2.CAP_PROP_SATURATION)*100)
  cv2.createTrackbar('CAP_PROP_SATURATION','setting',val,100, callback_saturation)
  val = int(cap.get(cv2.CAP_PROP_HUE)*100)
  cv2.createTrackbar('CAP_PROP_HUE','setting',val,100, callback_hue)
  val = int(cap.get(cv2.CAP_PROP_EXPOSURE)*100)
  cv2.createTrackbar('CAP_PROP_EXPOSURE','setting',val,100, callback_exposure)


# output setting file, get parameter
def output_params(cap, path):
  f=open(path,"w")
  val = cap.get(cv2.CAP_PROP_BRIGHTNESS)
  f.write("CAP_PROP_BRIGHTNESS:%.2f\n"%(val))
  val = cap.get(cv2.CAP_PROP_CONTRAST)
  f.write("CAP_PROP_CONTRAST:%.2f\n"%(val))
  val = cap.get(cv2.CAP_PROP_SATURATION)
  f.write("CAP_PROP_SATURATION:%.2f\n"%(val))
  val = cap.get(cv2.CAP_PROP_HUE)
  f.write("CAP_PROP_HUE:%.2f\n"%(val))
  val = cap.get(cv2.CAP_PROP_EXPOSURE)
  f.write("CAP_PROP_EXPOSURE:%.2f\n"%(val))
  f.close()

def put_text(image, str, pos=(0,20), size=1, thickness=1, color=(255, 255, 255)):
  cv2.putText(image, str, pos, cv2.FONT_HERSHEY_PLAIN,
    size, color, thickness, cv2.LINE_AA)

def put_param(cap, image, id, pos, frmtext):
  val = cap.get(id)
  put_text(image, frmtext%(val), pos)

def main(cap):
  global rec_writer
  rec_now = False
  while True:
    key = cv2.waitKey(1)
    # quit
    if key & 0xFF == ord('q'):
      break
    # write setting file
    if key & 0xFF == ord('w'):
      output_params(cap, PATH)
    
    # recording
    if key & 0xFF == ord('r'):
      if rec_now == False:
        rec_now = True
        tdatetime = dt.now()
        tstr = tdatetime.strftime('%Y%m%d-%H%M%S')
        media_file_name = "rec_{}.mp4".format(tstr)
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        rec_writer = cv2.VideoWriter(media_file_name, fourcc, FPS, (WIDTH, HEIGHT))
      else:
        rec_now = False
        if rec_writer != None:
          rec_writer.release()
          rec_writer = None

    # get frame, put text
    _, frame = cap.read()
    put_text(frame, "%.2f"%(time.time()), (0,20))
    put_text(frame, "%dx%d fps=%d"%(WIDTH, HEIGHT, FPS), (130,20))
    
    if rec_writer != None:
      put_text(frame, "REC", (280,20), thickness=2, color=(0, 0, 255))
      rec_writer.write(frame)

    # draw frame
    cv2.imshow('setting', frame)

  # finish
  cap.release()
  cv2.destroyAllWindows()
  if rec_writer != None:
    rec_writer.release()

if __name__ == '__main__':
  init(cap)
  build_trackbar(cap)

  # cap.set()が早すぎると
  # カメラのメモリ上にパラメータは設定できても
  # なぜかキャプチャ映像に反映されてない
  # このタイミングでcap.read()後に値を再設定すると反映される
  _, frame = cap.read()
  update_param(cap)

  main(cap)
