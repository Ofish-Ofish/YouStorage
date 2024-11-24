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
		self.reverse_mapping = {}

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

	def make_frequency_dict(self, text):
		frequency = {}
		for character in text:
			if not character in frequency:
				frequency[character] = 0
			frequency[character] += 1
		return frequency

	def make_heap(self, frequency):
		for key in frequency:
			node = self.HeapNode(key, frequency[key])
			heapq.heappush(self.heap, node)

	def merge_nodes(self):
		while(len(self.heap)>1):
			node1 = heapq.heappop(self.heap)
			node2 = heapq.heappop(self.heap)

			merged = self.HeapNode(None, node1.freq + node2.freq)
			merged.left = node1
			merged.right = node2

			heapq.heappush(self.heap, merged)


	def make_codes_helper(self, root, current_code):
		if(root == None):
			return

		if(root.char != None):
			self.codes[root.char] = current_code
			self.reverse_mapping[current_code] = root.char
			return

		self.make_codes_helper(root.left, current_code + "0")
		self.make_codes_helper(root.right, current_code + "1")


	def make_codes(self):
		root = heapq.heappop(self.heap)
		current_code = ""
		self.make_codes_helper(root, current_code)


	def get_encoded_text(self, text):
		encoded_text = ""
		for character in text:
			encoded_text += self.codes[character]
		return encoded_text


	def pad_encoded_text(self, encoded_text):
		extra_padding = 8 - len(encoded_text) % 8
		for i in range(extra_padding):
			encoded_text += "0"

		padded_info = "{0:08b}".format(extra_padding)
		encoded_text = padded_info + encoded_text
		return encoded_text


	def get_byte_array(self, padded_encoded_text):
		if(len(padded_encoded_text) % 8 != 0):
			print("Encoded text not padded properly")
			exit(0)

		b = bytearray()
		for i in range(0, len(padded_encoded_text), 8):
			byte = padded_encoded_text[i:i+8]
			b.append(int(byte, 2))
		return b


	def compress(self):
		filename, file_extension = os.path.splitext(self.path)

		with open(self.path, 'r+') as file:
			text = file.read()
			text = text.rstrip()

			frequency = self.make_frequency_dict(text)
			self.make_heap(frequency)
			self.merge_nodes()
			self.make_codes()

			encoded_text = self.get_encoded_text(text)
			padded_encoded_text = self.pad_encoded_text(encoded_text)
			return [padded_encoded_text, self.reverse_mapping]

def remove_padding(padded_encoded_text):
	padded_info = padded_encoded_text[:8]
	extra_padding = int(padded_info, 2)

	padded_encoded_text = padded_encoded_text[8:] 
	encoded_text = padded_encoded_text[:-1*extra_padding]

	return encoded_text

def decode_text(encoded_text, reverse_mapping):
	current_code = ""
	decoded_text = ""

	for bit in encoded_text:
		current_code += bit
		if(current_code in reverse_mapping):
			character = reverse_mapping[current_code]
			decoded_text += character
			current_code = ""

	return decoded_text

def decompress( bit_string, output_path, reverse_mapping):
  with open(output_path, 'w') as output:

    encoded_text = remove_padding(bit_string)

    decompressed_text = decode_text(encoded_text, reverse_mapping)
    
    output.write(decompressed_text)

  print("Decompressed")
  return output_path

def textToBinary(text):
    return ''.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))

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

def binaryToText(binary, n):
  byteList = [binary[i:i+n] for i in range(0, len(binary), n)]
  intList = [int(b, 2) for b in byteList]
  return bytes(intList).decode('utf-8', errors='replace')


def youtubeToVid(link, savePath, vidname):
  ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'outtmpl': f'{savePath}/{vidname}.%(ext)s',  
  }
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([link])

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

textdir = "iliad.txt"





if __name__ == "__main__":
	### text to vid ###
	h = HuffmanCoding(textdir)
	output, reverse_mapping  = h.compress()[0], h.compress()[1]
	reverseMappingPicAmount = ceil(len(textToBinary(str(reverse_mapping)))/(WIDTH/COMPRESSIONFACTOR * HEIGHT/COMPRESSIONFACTOR)/3)
	bitsToImgs(textToBinary(str(reverse_mapping)), COLORS, WIDTH, HEIGHT, COMPRESSIONFACTOR, "reverseMapping", "img/reverseMapping")
	breakPic(WIDTH, HEIGHT)
	bitsToImgs(output, COLORS, WIDTH, HEIGHT, COMPRESSIONFACTOR, "output", "img/textPics")
	imgsToVid("iliad.avi")

	# youtube download
	# youtubeToVid("https://youtu.be/BaRB4_nSwXo", ".", "bible")

	### vid to text ###
	vidToPics("bible.mkv")
	binary = picsToBinary( "img/textPics", HEIGHT, WIDTH, COMPRESSIONFACTOR, COLORS)
	text, reverseMapping = binary.split(maxsplit=1)
	reverseMapping = literal_eval(binaryToText(reverseMapping.strip(), 8))
	decompress(text , "decompressed.txt", reverseMapping)






#print(textToBinary(str(reverse_mapping)))

# bitsToImgs(textFileToBinary(textdir), colors, width, height, compressionFactor)
# imgsToVid(imgDir, vidname)


# decode_path = decompress(output , "decompressed.txt", reverse_mapping)

