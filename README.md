# YouStorage 🔁

## Table of Contents

1. [Introduction](#introduction)
2. [Warnings](#warnings)
3. [Project Explanation](#project-explanation)
4. [Dependencies](#dependencies)
5. [How to Contribute](#how-to-contribute)

## Introduction

YouStorage is a unique project that converts text files into video files and vice versa.

## Warnings

- **Data Loss**: This program may delete original files during the conversion process. data loss may also occur during the conversion process. Please ensure you have backups of your files before using this program. The creator of YouStorage is not responsible for any data loss.

- **User Agreements**: Do not use this program to breach any user agreements or terms of service. The creator of YouStorage is not responsible for any misuse of this software.

## Project Explanation

YouStorage has three main functionalities: converting text files into video files, converting video files into text files, and downloading videos from YouTube.

- **Text to Video**: The text file is encoded into binary using Huffman coding. The binary data is then converted into colored pixels (red, green, blue, and black) and compiled into images. A break image separates the text from the reverse mapping of the encoding, which is also stored as an image. All images are compiled into a video file. This process can increase the file size by up to 19000%.

- **Video to Text**: The video is read frame by frame, extracting binary data from the pixel colors. The binary data is decoded using the reverse mapping to reconstruct the original text file.

- **YouTube Video Download**: Videos are downloaded using the `yt-dlp` library and can be converted into text files using the same process as converting a video file into a text file.

## Dependencies

To run YouStorage, you need to install the following libraries:

- `Pillow`
- `opencv-python`
- `yt-dlp`
- `curses` (for Unix-based systems)
- `windows-curses` (for Windows systems)

Additionally, you need to have `ffmpeg` installed on your computer.

You can install the required Python libraries using pip

## How to Contribute

We welcome contributions to YouStorage! To contribute, follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes.
4. Submit a pull request with a detailed description of your changes.

Please ensure your code follows coding standards and includes appropriate tests.
