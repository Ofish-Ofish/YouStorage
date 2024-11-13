from PIL import Image, ImageDraw
import re
import os
import cv2 as cv
from math import ceil
import yt_dlp
from pprint import pprint
from multiprocessing import Pool, cpu_count
import time
import random

def binaryToText(binary, n):
  intList = []
  byteList = [binary[i:i+n] for i in range(0, len(binary), n)]
  for b  in byteList:
    intList.append(int(b, 2))
  return bytes(intList).decode('utf-8', errors='replace')

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
   

if __name__ == '__main__':
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
  with open("newBible.txt", "w", encoding="utf-8") as f:
    f.write(binaryToText(picsToBinary(IMGDIR, HEIGHT, WIDTH, COMPRESSIONFACTOR, COLORS), 8))
