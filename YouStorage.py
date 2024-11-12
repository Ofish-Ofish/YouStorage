from PIL import Image, ImageDraw
import re
import os
import cv2 as cv
from math import ceil
import yt_dlp
from pprint import pprint

def textToBinary(filedir):
  with open(filedir, "r", encoding='utf-8') as f:
    text = f.read()
    return ''.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))
  
def binaryToText(binary, n):
  intList = []
  byteList = [binary[i:i+n] for i in range(0, len(binary), n)]
  for b  in byteList:
    intList.append(int(b, 2))
  return bytes(intList).decode('utf-8', errors='replace')
  
def bitsToImg(binary, colors, width, height, compressionFactor):
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
    print('Read a new frame: ', success)
    count += 1
  os.chdir("..")
  vidcap.release()
  os.remove(vidName)

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

  for image in images:
    im = Image.open(image) 
    px = im.load()
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
        averageColor = [avgR/pixelNum, avgG/pixelNum, avgB/pixelNum,]
        
        distances = [(((averageColor[0] - color[0])**2 + (averageColor[1] - color[1])**2 + (averageColor[2] - color[2])**2)**(1/2)) for color in cleanColorValues]
        binary+=(colorKeys[colorValues.index(colorValues[distances.index(min(distances))])])
    os.remove(image)
  os.chdir("..")
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
  bitsToImg(textToBinary(TEXT), COLORS, WIDTH, HEIGHT, COMPRESSIONFACTOR)
  imgsToVid(IMGDIR, VIDNAME)
  # youtubeToVid("https://www.youtube.com/watch?v=2naim9F4010", SAVEPATH)
  vidToPics(VIDNAME)
  with open("newBible.txt", "w", encoding="utf-8") as f:
    f.write(binaryToText(picsToBinary(IMGDIR, HEIGHT, WIDTH, COMPRESSIONFACTOR, COLORS), 8))