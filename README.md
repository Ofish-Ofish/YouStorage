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

YouStorage converts text files into video files by encoding the text into binary and then representing that binary data as colored pixels in images. These images are then compiled into a video. The process significantly increases the file size, potentially by up to 40000%. The project also supports converting videos back into text files by decoding the binary data from the video frames. additonally the project supports downloading videos from youtube for test purposes.

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

Please ensure your code follows our coding standards and includes appropriate tests.
