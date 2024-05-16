## Overview
* This script will label a folder of jpg files using the color of the object compared to the color of the background
* Images with more complex backgrounds may not produce expected results
* The more unique the colors of the images are, the greater chaces the images will be identified properly

## To Run:
First install the requirements.txt: 

    pip install -r /path/to/requirements.txt 

Than modify and run the the main.py script

## Main.py
This script uses the labeler module to label images based on their pixel colors. It uses a predefined palette of colors to identify specific subjects in the images.
Configuration

    palette: a list of RGB color values used to identify subjects in the images.
    linkToFolder: the path to a folder containing only .jpg images to be labeled.
    topPixel, bottomPixel, leftPixel, rightPixel: the expected colors of the top, bottom, left, and right pixels of the images, respectively. These colors must be included in the palette.

Note

    The color values are in RGB format, with each value ranging from 0 to 255.
    The colors in the palette are used to identify specific subjects in the images, with a greater variety of colors increasing the probability of accurate identification.
    The script assumes that the images in the specified folder are in .jpg format only.
    Do not Delete the Label and Subject folders

Example input image:
![fcone4](https://github.com/SgainsO/YOLO_Single_Object_Labeler/assets/126195012/997cd2c3-7c9d-4363-a10d-32441b9ab344)
