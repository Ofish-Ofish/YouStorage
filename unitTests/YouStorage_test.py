import sys
sys.path.append('..')

from YouStorage import validPath, textToBinary, binaryToText, bitsToImgs, imgsToVid, youtubeToVid, vidToPics, picsToBinary, picToBinary


def validPath_test():
  assert validPath("YouStorage_test.txt") == False

def textToBinary_test():
  assert textToBinary("שלום I'm 🚀") == "1101011110101001110101111001110011010111100101011101011110011101001000000100100100100111011011010010000011110000100111111001101010000000"

def binaryToText_test():
  assert binaryToText("111001001011110110100000111001011010010110111101001000000100100100100111011011010010000011110000100111111010101110000011") == "你好 I'm 🫃"

def bitsToImgs_test():
  pass

def imgsToVid_test():
  pass

def youtubeToVid_test():
  pass

def vidToPics_test():
  pass

def picsToBinary_test():
  pass

def picToBinary_test():
  pass