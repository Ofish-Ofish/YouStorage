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

def dot12():
    global animationFinished
    for c in itertools.cycle([
      "⢀⠀ ","⡀⠀ ","⠄⠀ ","⢂⠀ ","⡂⠀ ","⠅⠀ ","⢃⠀ ","⡃⠀ ","⠍⠀ ","⢋⠀ ","⡋⠀ ","⠍⠁ ","⢋⠁ ","⡋⠁ ","⠍⠉ ","⠋⠉ ",
			"⠋⠉ ","⠉⠙ ","⠉⠙ ","⠉⠩ ","⠈⢙ ","⠈⡙ ","⢈⠩ ","⡀⢙ ","⠄⡙ ","⢂⠩ ","⡂⢘ ","⠅⡘ ","⢃⠨ ","⡃⢐ ","⠍⡐ ","⢋⠠ ",
			"⡋⢀ ","⠍⡁ ","⢋⠁ ","⡋⠁ ","⠍⠉ ","⠋⠉ ","⠋⠉ ","⠉⠙ ","⠉⠙ ","⠉⠩ ","⠈⢙ ","⠈⡙ ","⠈⠩ ","⠀⢙ ","⠀⡙ ","⠀⠩ ",
			"⠀⢘ ","⠀⡘ ","⠀⠨ ","⠀⢐ ","⠀⡐ ","⠀⠠ ","⠀⢀ ","⠀⡀ "
      ]):
        if animationFinished:
            break
        sys.stdout.write('\rloading ' + c)
        sys.stdout.flush()
        time.sleep(0.03)

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
  video = cv.VideoWriter(vidName, 0, 60, (WIDTH, HEIGHT))  

  for image in images:  
    video.write(cv.imread(os.path.join(imgFolder, image))) 
    os.remove(f"img/{image}")

  cv.destroyAllWindows() 
  video.release()

def youtubeToVid(link, savePath, vidname):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{savePath}/{vidname}.%(ext)s',  
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
  
  os.chdir("..")
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

def choose(stdscr, question, options):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.curs_set(0)

    current_row = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, question, curses.A_BOLD)
        for idx, option in enumerate(options):
            color_pair = 2 if idx == current_row else 1
            stdscr.attron(curses.color_pair(color_pair))
            stdscr.addstr(idx + 1, 0, f"{'>' if idx == current_row else ' '} {option}")
            stdscr.attroff(curses.color_pair(color_pair))
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == ord("\n"):
            break

    return current_row

def intro():
  print(r'_____.___.             _________ __                                      ')
  print(r'\__  |   | ____  __ __/   _____//  |_  ________________     ____   ____  ')
  print(r' /   |   |/  _ \|  |  \_____  \\   __\/  _ \_  __ \__  \   / ___\_/ __ \ ')
  print(r' \____   (  <_> )  |  /        \|  | (  <_> )  | \// __ \_/ /_/  >  ___/ ')
  print(r' / ______|\____/|____/_______  /|__|  \____/|__|  (____  /\___  / \___  >')
  print(r' \/                          \/                        \//_____/      \/ ')
  time.sleep(2)

  print("Welcome to YouStorage! This program will convert any text file into a video file and vice versa.")
  time.sleep(3)
  print("This program is not responsible for any loss of data. Please make sure to back up your files before using this program.")
  time.sleep(3)
  print("Please make sure to have ffmpeg installed on your computer before using this program.")
  time.sleep(3)
  os.system('cls' if os.name == 'nt' else 'clear')

def main(colors, width, height, compressionFactor, imgDir):
  global animationFinished
  answer = curses.wrapper(lambda stdscr: choose(stdscr, "What would you like to do" , ["Convert text to video", "Convert video to text", "download a youtube video"]))

  if answer == 0:
    textdir = input("Please enter the path of the text file you would like to convert: ")
    os.system('cls' if os.name == 'nt' else 'clear')
    vidname = input("Please enter the name of the video file you would like to save: ")
    vidname = vidname + ".avi"
    os.system('cls' if os.name == 'nt' else 'clear')
    answer = curses.wrapper(lambda stdscr: choose(stdscr, "would you like this program to delete the original text file" , ["yes", "no"]))
    os.system('cls' if os.name == 'nt' else 'clear')

    animationFinished = False
    t = threading.Thread(target=dot12, )
    t.start()
    try:
      bitsToImgs(textToBinary(textdir), colors, width, height, compressionFactor)
      imgsToVid(imgDir, vidname)
    except:
      animationFinished = True
      print("error encountered try again")
      quit()

    animationFinished = True
    os.system('cls' if os.name == 'nt' else 'clear')
    if answer == 0:
      os.remove(textdir)

    print("Conversion complete!")

  elif answer == 1:
    print("WARNING! This will delete the original video file. Make sure to back up your files before proceeding.")
    time.sleep(5)
    
    vidname = input("Please enter the path of the video file you would like to convert: ")
    os.system('cls' if os.name == 'nt' else 'clear')
    textname = input("Please enter the name of the text file you would like to save: ")
    textname = textname + ".txt"
    os.system('cls' if os.name == 'nt' else 'clear')  

    animationFinished = False
    t = threading.Thread(target=dot12, )
    t.start()

    try:
      vidToPics(vidname)
      with open(textname, "w", encoding="utf-8") as f:
        f.write(binaryToText(picsToBinary(imgDir, height, width, compressionFactor, colors), 8))
    except:
      animationFinished = True
      print("error encountered try again")
      quit()

    animationFinished = True
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Conversion complete!")
  
  elif answer == 2:
    url = input("Please enter the url of the youtube video you would like to download: ")
    os.system('cls' if os.name == 'nt' else 'clear')  
    vidname = input("Please enter the name of the video file you would like to save: ")
    os.system('cls' if os.name == 'nt' else 'clear')  
    youtubeToVid(url, ".", vidname)

if __name__ == "__main__":
  IMGDIR = "img"
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
  COMPRESSIONFACTOR = 10

  animationFinished = False
  running = True

  os.system('cls' if os.name == 'nt' else 'clear')
  intro()

  while running:
    main(COLORS, WIDTH, HEIGHT, COMPRESSIONFACTOR, IMGDIR)
    time.sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')
    answer = curses.wrapper(lambda stdscr: choose(stdscr, "would you like to continue using YouStorage" , ["yes", "no"]))
    if answer == 1:
       running = False
    os.system('cls' if os.name == 'nt' else 'clear')