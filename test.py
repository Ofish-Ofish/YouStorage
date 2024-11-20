from PIL import Image, ImageDraw
import os
import cv2 as cv
from math import ceil
import yt_dlp
from multiprocessing import Pool, cpu_count
import time
import sys
import itertools
import threading
import curses

def makeFreqDict(text):
  freq = {}
  for char in text:
    if not char in freq:
      freq[char] = 0
    freq[char] += 1
  return freq

def makeHeap(freq):
  heap = []
  
  
def mergeCodes():

def assignCodes():

def getEncodedText(text):

def paddding(encodedText):

def GetByteArray(paddedEncodedText):

def compress(path):
  fileName, fileExtension = os.path.splitext(path)
  outputPath = fileName + ".bin"

  with open(path, 'r') as f, open(outputPath, 'wb') as o:
    text = f.read()
    text.rstrip()

    freq = makeFreqDict(text)

    heap = makeHeap(freq)

    mergeCodes()
    assignCodes()
    encodedText = getEncodedText(text)
    paddedEncodedText = paddding(encodedText)

    b = getEncodedText(paddedEncodedText)

    o.write(bytes(b))
  
  print("compressed")
  return outputPath


