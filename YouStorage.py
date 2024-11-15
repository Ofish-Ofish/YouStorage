from PIL import Image, ImageDraw
import re
import os
import cv2 as cv
from math import ceil
import yt_dlp
from multiprocessing import Pool, cpu_count
import time
import sys
import itertools
import threading

def dot12():
    global animationFinished
    for c in itertools.cycle([
      "⢀⠀ ",
			"⡀⠀ ",
			"⠄⠀ ",
			"⢂⠀ ",
			"⡂⠀ ",
			"⠅⠀ ",
			"⢃⠀ ",
			"⡃⠀ ",
			"⠍⠀ ",
			"⢋⠀ ",
			"⡋⠀ ",
			"⠍⠁ ",
			"⢋⠁ ",
			"⡋⠁ ",
			"⠍⠉ ",
			"⠋⠉ ",
			"⠋⠉ ",
			"⠉⠙ ",
			"⠉⠙ ",
			"⠉⠩ ",
			"⠈⢙ ",
			"⠈⡙ ",
			"⢈⠩ ",
			"⡀⢙ ",
			"⠄⡙ ",
			"⢂⠩ ",
			"⡂⢘ ",
			"⠅⡘ ",
			"⢃⠨ ",
			"⡃⢐ ",
			"⠍⡐ ",
			"⢋⠠ ",
			"⡋⢀ ",
			"⠍⡁ ",
			"⢋⠁ ",
			"⡋⠁ ",
			"⠍⠉ ",
			"⠋⠉ ",
			"⠋⠉ ",
			"⠉⠙ ",
			"⠉⠙ ",
			"⠉⠩ ",
			"⠈⢙ ",
			"⠈⡙ ",
			"⠈⠩ ",
			"⠀⢙ ",
			"⠀⡙ ",
			"⠀⠩ ",
			"⠀⢘ ",
			"⠀⡘ ",
			"⠀⠨ ",
			"⠀⢐ ",
			"⠀⡐ ",
			"⠀⠠ ",
			"⠀⢀ ",
			"⠀⡀ "
      ]):
        if animationFinished:
            break
        sys.stdout.write('\rloading ' + c)
        sys.stdout.flush()
        time.sleep(0.04)

def textToBinary(filedir):
  with open(filedir, "r", encoding='utf-8') as f:
    text = f.read()
    return ''.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))
  
def binaryToText(binary, n):
  byteList = [binary[i:i+n] for i in range(0, len(binary), n)]
  intList = [int(b, 2) for b in byteList]
  return bytes(intList).decode('utf-8', errors='replace')
  
def bitsToImgs(binary, colors, width, height, compressionFactor):
    threeBit = [binary[i:i+3] for i in range(0, len(binary), 3)]
    threeBitLen = len(threeBit)

    os.makedirs("img", exist_ok=True)
    os.chdir("img")

    scaledWidth = width // compressionFactor
    scaledHeight = height // compressionFactor
    pixelsPerFrame = scaledWidth * scaledHeight

    for i in range(ceil(threeBitLen/pixelsPerFrame)):
      img = Image.new('RGB', (width, height), '#808080')
      draw = ImageDraw.Draw(img)

      for j in range(scaledHeight):
        for k in range(scaledWidth):
          idx = i * pixelsPerFrame + j * scaledWidth + k

          if idx < threeBitLen:
            color = colors.get(threeBit[idx], "#808080")
            x = k * compressionFactor
            y = j * compressionFactor
            draw.rectangle([x,y,x + compressionFactor - 1,y + compressionFactor -1], fill=color)
          else:
            break
      img.save(f'myImg{i}.png')

    os.chdir("..")
    time.sleep(.1)

def imgsToVid(imgFolder, vidName):
  images = [f"myimg{n}.png" for n in list(range(0,len(os.listdir(imgFolder))))]
  video = cv.VideoWriter(vidName, 0, 1, (WIDTH, HEIGHT))  

  for image in images:  
    video.write(cv.imread(os.path.join(imgFolder, image))) 
    os.remove(f"img/{image}")

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
    count += 1

  os.chdir("..")
  vidcap.release()
  os.remove(vidName)
  time.sleep(.1)

def picsToBinary(imgFolder, height, width, compressionFactor, colors):
  binary = ""
  scaledWidth = width // compressionFactor
  scaledHeight = height // compressionFactor
  images = [f"frame{n}.png" for n in list(range(0,len(os.listdir(imgFolder))))]
  os.chdir("img")
  colors[""] = "#808080"

  colorKeys = list(colors.keys())
  cleanColorValues = [tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for color in colors.values()]
  colorValues = list(colors.values())
  pool = Pool(processes=(cpu_count() - 1))
  binaryList = [pool.apply_async(picToBinary, args=(image, scaledHeight, scaledWidth, compressionFactor, colorKeys, cleanColorValues, colorValues)) for image in images]

  pool.close()
  pool.join()

  for res in binaryList:
    binary += res.get()

  return binary 

def picToBinary(image, scaledHeight, scaledWidth, compressionFactor, colorKeys, cleanColorValues, colorValues):
    im = Image.open(image) 
    px = im.load()
    binary = ""

    for j in range(scaledHeight):
      for k in range(scaledWidth):
        pixelGroup = []
        for m in range(compressionFactor):
          for n in range(compressionFactor):
            pixelGroup.append(px[k * compressionFactor + m, j * compressionFactor + n])

        avgR, avgG, avgB = 0, 0, 0

        for pixel in pixelGroup:
          avgR += pixel[0]
          avgG += pixel[1]
          avgB += pixel[2]

        pixelNum = len(pixelGroup)
        averageColor = [avgR/pixelNum, avgG/pixelNum, avgB/pixelNum]

        distances = [(((averageColor[0] - color[0])**2 + (averageColor[1] - color[1])**2 + (averageColor[2] - color[2])**2)**(1/2)) for color in cleanColorValues]

        binary+=(colorKeys[colorValues.index(colorValues[distances.index(min(distances))])])
    os.remove(image)
    return binary  

if __name__ == "__main__":
  TEXT = "bible.txt"
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
  COMPRESSIONFACTOR = 2

  animationFinished = False

  t = threading.Thread(target=dot12, )
  t.start()

  starttime = time.time()
  bitsToImgs(textToBinary(TEXT), COLORS, WIDTH, HEIGHT, COMPRESSIONFACTOR)
  imgsToVid(IMGDIR, VIDNAME)
  # youtubeToVid("https://www.youtube.com/watch?v=2naim9F4010", SAVEPATH)
  vidToPics(VIDNAME)
  with open("newBible.txt", "w", encoding="utf-8") as f:
    f.write(binaryToText(picsToBinary(IMGDIR, HEIGHT, WIDTH, COMPRESSIONFACTOR, COLORS), 8))

  animationFinished = True
  os.system('cls' if os.name == 'nt' else 'clear')
  print("Time taken: ", time.time() - starttime)