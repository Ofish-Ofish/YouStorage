def encode(filedir):
  with open(filedir, "r", encoding='utf-8') as f:
    text = f.read()
    return ' '.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))

def decode(binary):
  byte_list = []
  for b  in binary.split():
    byte_list.append(int(b, 2))

  return bytes(byte_list).decode('utf-8')


if __name__ == "__main__":
    FILEDIR = "test.txt"
    print(encode(FILEDIR))
    print(decode(encode(FILEDIR)))
