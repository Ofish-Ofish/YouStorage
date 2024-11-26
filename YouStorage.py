import heapq
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
from PIL import Image, ImageDraw
from ast import literal_eval

class HuffmanCoding:
	def __init__(self, path):
		self.path = path
		self.heap = []
		self.codes = {}
		self.reverseMapping = {}

	class HeapNode:
		def __init__(self, char, freq):
			self.char = char
			self.freq = freq
			self.left = None
			self.right = None

		def __lt__(self, other):
			return self.freq < other.freq

		def __eq__(self, other):
			if(other == None):
				return False
			if(not isinstance(other, HeapNode)):
				return False
			return self.freq == other.freq

	def makeFreqDict(self, text):
		freq = {}
		for chr in text:
			if not chr in freq:
				freq[chr] = 0
			freq[chr] += 1
		return freq

	def makeHeap(self, freq):
		for key in freq:
			node = self.HeapNode(key, freq[key])
			heapq.heappush(self.heap, node)

	def mergeNodes(self):
		while(len(self.heap)>1):
			node1 = heapq.heappop(self.heap)
			node2 = heapq.heappop(self.heap)

			merged = self.HeapNode(None, node1.freq + node2.freq)
			merged.left = node1
			merged.right = node2

			heapq.heappush(self.heap, merged)


	def makeCodesHelper(self, root, currentCode):
		if(root == None):
			return

		if(root.char != None):
			self.codes[root.char] = currentCode
			self.reverseMapping[currentCode] = root.char
			return

		self.makeCodesHelper(root.left, currentCode + "0")
		self.makeCodesHelper(root.right, currentCode + "1")


	def makeCodes(self):
		root = heapq.heappop(self.heap)
		currentCode = ""
		self.makeCodesHelper(root, currentCode)


	def getEncodedText(self, text):
		encodedText = ""
		for character in text:
			encodedText += self.codes[character]
		return encodedText


	def padEncodedText(self, encodedText):
		extraPadding = 8 - len(encodedText) % 8
		for i in range(extraPadding):
			encodedText += "0"

		paddedInfo = "{0:08b}".format(extraPadding)
		encodedText = paddedInfo + encodedText
		return encodedText

	def compress(self):
		with open(self.path, 'r+') as file:
			text = file.read()
			text = text.rstrip()

			frequency = self.makeFreqDict(text)
			self.makeHeap(frequency)
			self.mergeNodes()
			self.makeCodes()

			encodedText = self.getEncodedText(text)
			paddedEncodedText = self.padEncodedText(encodedText)
			return [paddedEncodedText, self.reverseMapping]

def removePadding(paddedEncodedText):
	paddedInfo = paddedEncodedText[:8]
	extraPadding = int(paddedInfo, 2)

	paddedEncodedText = paddedEncodedText[8:] 
	encodedText = paddedEncodedText[:-1*extraPadding]

	return encodedText

def decodeText(encodedText, reverseMapping):
	currentCode = ""
	decodedText = ""

	for bit in encodedText:
		currentCode += bit
		if(currentCode in reverseMapping):
			character = reverseMapping[currentCode]
			decodedText += character
			currentCode = ""

	return decodedText

def decompress( bitString, outputPath, reverseMapping):
  with open(outputPath, 'w') as output:

    encodedText = removePadding(bitString)

    decompressedText = decodeText(encodedText, reverseMapping)
    
    output.write(decompressedText)

  print("Decompressed")
  return outputPath

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

def textToBinary(text):
    return ''.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))
 
def binaryToText(binary, n):
  byteList = [binary[i:i+n] for i in range(0, len(binary), n)]
  intList = [int(b, 2) for b in byteList]
  return bytes(intList).decode('utf-8', errors='replace')
  
def bitsToImgs(binary, colors, width, height, compressionFactor, picnames, imageSavePath):
  threeBit = [binary[i:i+2] for i in range(0, len(binary), 2)]
  threeBitLen = len(threeBit)

  os.makedirs(imageSavePath, exist_ok=True)
  

  scaledWidth = width // compressionFactor
  scaledHeight = height // compressionFactor
  pixelsPerFrame = scaledWidth * scaledHeight

  for i in range(ceil(threeBitLen/pixelsPerFrame)):
    img = Image.new('RGB', (width, height), '#FFFFFF')
    draw = ImageDraw.Draw(img)

    for j in range(scaledHeight):
      for k in range(scaledWidth):
        idx = i * pixelsPerFrame + j * scaledWidth + k

        if idx < threeBitLen:
          color = colors.get(threeBit[idx], "#FFFFFF")
          x = k * compressionFactor
          y = j * compressionFactor
          draw.rectangle([x,y,x + compressionFactor - 1,y + compressionFactor -1], fill=color)
        else:
          break
    img.save(f'{imageSavePath}/{picnames}{i}.png')

def breakPic(width, height):
	os.chdir("img")
	img = Image.new('RGB', (width, height), '#FFFFFF')
	img.save(f"breakPic.png")
	os.chdir("..")

def imgsToVid(vidName):
	images = [f"output{n}.png" for n in list(range(0,len(os.listdir("img/textPics"))))]
	reverseMapping = [f"reverseMapping{n}.png" for n in list(range(0,len(os.listdir("img/reverseMapping"))))]
	video = cv.VideoWriter(vidName, 0, 60, (WIDTH, HEIGHT))  

	for image in images:  
		video.write(cv.imread(os.path.join("img/textPics", image))) 
		os.remove(f"img/textPics/{image}")

	video.write(cv.imread(os.path.join("img", "breakPic.png"))) 
	os.remove(f"img/breakPic.png")

	for reversemap in reverseMapping:  
		video.write(cv.imread(os.path.join("img/reverseMapping", reversemap))) 
		os.remove(f"img/reverseMapping/{reversemap}")

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

  while success:
    cv.imwrite("img/textPics/frame%d.png" % count, image)         
    success,image = vidcap.read()
    count += 1

  vidcap.release()
  os.remove(vidName)
  time.sleep(.1)

def picsToBinary(imgFolder, height, width, compressionFactor, colors):
	binary = ""
	scaledWidth = width // compressionFactor
	scaledHeight = height // compressionFactor
	images = [f"frame{n}.png" for n in list(range(0,len(os.listdir(imgFolder))))]
	os.chdir(imgFolder)
	colors[" "] = "#FFFFFF"
	
	colorKeys = list(colors.keys())
	cleanColorValues = [tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) for color in colors.values()]
	colorValues = list(colors.values())
	pool = Pool(processes=(cpu_count() - 1))
	binaryList = [pool.apply_async(picToBinary, args=(image, scaledHeight, scaledWidth, compressionFactor, colorKeys, cleanColorValues, colorValues)) for image in images]

	pool.close()
	pool.join()

	for res in binaryList:
		binary += res.get()
	
	os.chdir("../..")
     
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

def validPath(path):
  if not os.path.exists(path):
    print(f"The file {path} does not exist.")
    return False
  if not os.access(path, os.R_OK):
    print(f"The file {path} is not readable.")
    return False
  return True

def main(colors, width, height, compressionFactor, imgDir):
  global animationFinished
  answer = curses.wrapper(lambda stdscr: choose(stdscr, "What would you like to do" , ["Convert text to video", "Convert video to text", "download a youtube video"]))

  if answer == 0:
    textdir = input("Please enter the text file name and file extension you would like to convert: ")
    if not validPath(textdir):
      return

    if not textdir.endswith(".txt"):
      print("The file must be a text file.")
      return
    
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
      h = HuffmanCoding(textdir)
      output, reverseMapping  = h.compress()[0], h.compress()[1]
      reverseMappingPicAmount = ceil(len(textToBinary(str(reverseMapping)))/(width/compressionFactor * height/compressionFactor)/3)
      bitsToImgs(textToBinary(str(reverseMapping)), colors, width, height, compressionFactor, "reverseMapping", "img/reverseMapping")
      breakPic(width, height)
      bitsToImgs(output, colors, width, height, compressionFactor, "output", "img/textPics")
      imgsToVid(vidname)


      # bitsToImgs(textFileToBinary(textdir), colors, width, height, compressionFactor)
      # imgsToVid(imgDir, vidname)
    except:
      animationFinished = True
      print("error encountered try again")
      return

    animationFinished = True
    os.system('cls' if os.name == 'nt' else 'clear')

    if answer == 0:
      os.remove(textdir)

    print("Conversion complete!")

  elif answer == 1:
    print("WARNING! This will delete the original video file. Make sure to back up your files before proceeding.")
    time.sleep(5)
    
    vidname = input("Please enter the reletive path of the video file you would like to convert: ")
    if not validPath(vidname):
      return
    
    validVidFormats = [".avi", ".mp4", ".mov", ".webm", ".mkv"]
    if not any(vidname.endswith(format) for format in validVidFormats):
      print("The file must be a video file.")
      return

    os.system('cls' if os.name == 'nt' else 'clear')
    textdir = input("Please enter the text file name and file extension you would like to convert: ")

    if not textdir.endswith(".txt"):
      print("The file must be a text file.")
      return
    os.system('cls' if os.name == 'nt' else 'clear')  

    animationFinished = False
    t = threading.Thread(target=dot12, )
    t.start()

    try:
      vidToPics(vidname)
      binary = picsToBinary( "img/textPics", height, width, compressionFactor, colors)
      text, reverseMapping = binary.split(maxsplit=1)
      reverseMapping = literal_eval(binaryToText(reverseMapping.strip(), 8))
      decompress(text , textdir, reverseMapping)
         

      # vidToPics(vidname)
      # with open(textname, "w", encoding="utf-8") as f:
      #   f.write(binaryToText(picsToBinary(imgDir, height, width, compressionFactor, colors), 8))
    except:
      animationFinished = True
      print("error encountered try again")
      return

    animationFinished = True
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Conversion complete!")
  
  elif answer == 2:
    url = input("Please enter the url of the youtube video you would like to download: ")
    os.system('cls' if os.name == 'nt' else 'clear')  
    vidname = input("Please enter the name of the video file you would like to save: ")
    os.system('cls' if os.name == 'nt' else 'clear')  
    try:
      youtubeToVid(url, ".", vidname)
    except:
      print("error encountered try again")
      return

if __name__ == "__main__":
  IMGDIR = "img"
  COLORS = {	
    "00": "#FF0000", 
    "01": "#00FF00",
    "10": "#0000FF",
    "11": "#000000"

  }

  WIDTH = 1920
  HEIGHT = 1080
  COMPRESSIONFACTOR = 8

  animationFinished = False
  running = True


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