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
  return bytes(intList).decode('utf-8')
  
def bitsToImg(binary, colors, frameSize, width, height, compressionFactor):
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

def picsToBinary(pic, height, width, frameSize, compressionFactor, colors):
  threeBit = []
  pixels = []
  im = Image.open(pic) 
  px = im.load()

  scaledWidth = width // compressionFactor
  scaledHeight = height // compressionFactor
  pixelsPerFrame = scaledWidth * scaledHeight

  for j in range(scaledHeight):
    for k in range(scaledWidth):
      #ths code will have to be manually adjusted based on the compression factor. i cant think of a solution that doesnt require manual imput right now.
      pixelGroup = [
        px[k * compressionFactor, j * compressionFactor],
        px[k * compressionFactor + 1, j * compressionFactor],
        px[k * compressionFactor, j * compressionFactor + 1],
        px[k * compressionFactor + 1, j * compressionFactor + 1]
      ]

      avgR = [pixelGroup[0][0], pixelGroup[1][0], pixelGroup[2][0], pixelGroup[3][0]]
      avgG = [pixelGroup[0][1], pixelGroup[1][1], pixelGroup[2][1], pixelGroup[3][1]]
      avgB = [pixelGroup[0][2], pixelGroup[1][2], pixelGroup[2][2], pixelGroup[3][2]]

      averageColor = [
        sum(avgR)/len(avgR),
        sum(avgG)/len(avgG),
        sum(avgB)/len(avgB),
      ]

      distances = []
      for color in colors.values():
        color = color.lstrip('#')
        color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        distances.append((((averageColor[0] - color[0])**2 + (averageColor[1] - color[1])**2 + (averageColor[2] - color[2])**2)**(1/2)))
      # print(averageColor, distances, distances.index(min(distances)), list(colors.values())[distances.index(min(distances))])
      # print(list(colors.keys())[list(colors.values()).index(list(colors.values())[distances.index(min(distances))])])
      threeBit.append(list(colors.keys())[list(colors.values()).index(list(colors.values())[distances.index(min(distances))])])
      quit()

  return pixels
      


if __name__ == "__main__":
  TEXT = "book.txt"
  IMGDIR = "img"
  VIDNAME = "bible.mp4v"
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
  COMPRESSIONFACTOR = 2
  # bitsToImg(textToBinary(TEXT), COLORS, FRAMESIZE, WIDTH, HEIGHT, COMPRESSIONFACTOR)
  # imgsToVid(IMGDIR, VIDNAME)
  # youtubeToVid("https://www.youtube.com/watch?v=2naim9F4010", SAVEPATH)
  # vidToPics(VIDNAME)
  pprint(picsToBinary("img/frame0.png", HEIGHT, WIDTH, FRAMESIZE, COMPRESSIONFACTOR, COLORS))