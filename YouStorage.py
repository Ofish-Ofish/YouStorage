from PIL import Image, ImageDraw
import re
import os
import cv2 as cv
from math import ceil
import yt_dlp

def textToBinary(filedir):
  with open(filedir, "r", encoding='utf-8') as f:
    text = f.read()
    return ''.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))
  
def binaryToText(binary, n):
  intList = []
  byteList = [binary[i:i+n] for i in range(0, len(binary), n)]
  for b  in byteList:
    intList.append(int(b, 2))
  return bytes(intList).decode('utf-8')
  
def bitsToImg(binary, colors, frameSize, width, height):
    threeBit = [binary[i:i+3] for i in range(0, len(binary), 3)]
    threeBitLen = len(threeBit)

    os.makedirs("img", exist_ok=True)
    os.chdir("img")
    for i in range(ceil(threeBitLen/frameSize)):
      img = Image.new('RGB', (width, height), '#808080')
      draw = ImageDraw.Draw(img)

      for j in range(height):
        for k in range(width):
          idx = i * frameSize + j * width + k
          if idx < threeBitLen:
            color = colors.get(threeBit[idx], "#808080")
            draw.point((k, j), fill=color)
          else:
            break
      img.save(f'myImg{i}.png')
    os.chdir("..")

def imgToVid(imgFolder, vidName):
  images = [img for img in os.listdir(imgFolder)] 

  video = cv.VideoWriter(vidName, 0, 1, (WIDTH, HEIGHT))  
  for image in images:  
    video.write(cv.imread(os.path.join(imgFolder, image))) 

  cv.destroyAllWindows() 
  video.release()

def youtubeToVid(link, savePath):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{savePath}/%(title)s.%(ext)s',  
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def vidToPics(vidName):
  vidcap = cv.VideoCapture(vidName)
  success,image = vidcap.read()
  count = 0
  os.chdir("img")
  while success:
    cv.imwrite("frame%d.png" % count, image)         
    success,image = vidcap.read()
    print('Read a new frame: ', success)
    count += 1
  os.chdir("..")

def picToBinary(pic):
  im = Image.open(pic) 
  pix = im.load()
  print (pix[0,0])


if __name__ == "__main__":
  TEXT = "book.txt"
  IMGDIR = "img"
  VIDNAME = "bible.avi"
  SAVEPATH = "."
  COLORS = {
     "000" : "#000000",
     "001" : "#FF0000",
     "010" : "#00FF00",
     "011" : "#FFFF00",
     "100" : "#0000FF",
     "101" : "#FF00FF",
     "110" : "#00FFFF",
     "111" : "#FFFFFF",

  }
  WIDTH = 1920
  HEIGHT = 1080
  FRAMESIZE = WIDTH * HEIGHT
  # bitsToImg(textToBinary(TEXT), COLORS, FRAMESIZE, WIDTH, HEIGHT)
  # imgToVid(IMGDIR, VIDNAME)
  # youtubeToVid("https://www.youtube.com/watch?v=2naim9F4010", SAVEPATH)
  vidToPics(VIDNAME)
  picToBinary("img/frame0.png")