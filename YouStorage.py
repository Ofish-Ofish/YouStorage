from PIL import Image, ImageDraw
import re
from math import ceil

def encode(filedir):
  with open(filedir, "r", encoding='utf-8') as f:
    text = f.read()
    return ''.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))

def decode(binary, n):
  intList = []
  byteList = [binary[i:i+n] for i in range(0, len(binary), n)]
  for b  in byteList:
    intList.append(int(b, 2))
  return bytes(intList).decode('utf-8')


if __name__ == "__main__":
  FILEDIR = "book.txt"
  # print(encode(FILEDIR))
  # print(decode(encode(FILEDIR), 8))

  colors = {
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
  frameSize = WIDTH * HEIGHT

  bytestr = encode(FILEDIR)
  threeBit = [bytestr[i:i+3] for i in range(0, len(bytestr), 3)]
  threeBitLen = len(threeBit)

  for i in range(ceil(threeBitLen/frameSize)):
    img = Image.new('RGB', (WIDTH, HEIGHT), '#808080')
    draw = ImageDraw.Draw(img)
    for j in range(HEIGHT):
      for k in range(WIDTH):
        idx = i * frameSize + j * WIDTH + k
        if idx < threeBitLen:
          color = colors.get(threeBit[idx], "#808080")
          draw.point((k, j), fill=color)
        else:
          break
    img.save(f'my_image{i}.png')





  # print(threeBit)

  # for i in range(1000):
    # draw.point((i, i), fill=colors["000"])

  # Save the image
  # img.save('my_image.png')
