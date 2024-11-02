with open("test.txt", "r", encoding='utf-8') as f:
  text = f.read()
  binary_text = ' '.join(format(byte, '08b') for char in text for byte in char.encode('utf-8'))
  print(binary_text)
