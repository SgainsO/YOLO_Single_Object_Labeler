import cv2
import os
import shutil
import numpy as np
from PIL import Image

#Annotate yolo using python https://www.youtube.com/watch?v=1d7u8wTmA80


Shape = (256,256)


def holding():
    coneCv = np.array(cone)
    coneCv = cv2.cvtColor(coneCv, cv2.COLOR_BGR2RGB)
    cv2.imshow('Preproccessed', coneCv)
    cv2.waitKey(0) 

def imagePreproccessing(pal, name):          #
    palette = pal 

    palImg = Image.new('P', (16,16))
    palImg.putpalette(palette * (len(palette) // 3))         #Put the palette into image form     


    cone = Image.open(name)
    
    cone = cone.resize(Shape)

    cone  = cone.quantize(palette=palImg, dither=0)         # Use the palette to quantize the image

    coneCv = np.array(cone.convert('RGB'))
    coneCv = cv2.cvtColor(coneCv, cv2.COLOR_BGR2RGB)

    return coneCv

def makeLabelFile(textFile, x, y, width, height):
    cwd = os.getcwd
    os.chdir("labels")
    file = open(textFile, "w")
    file.write(f"{0} {x} {y} {width} {height}")
    file.close()
    os.chdir("..")



def findRequiredCords(CvImg, name):
  #  cv2.imshow("test", CvImg)
  #  cv2.waitKey(0)
  #  cv2.destroyAllWindows()
    
    imageHeight, imageWidth, channels = CvImg.shape
    height = findHeight(CvImg, imageWidth, imageHeight)
    width, StartChord = findWidth(CvImg, imageWidth, imageHeight)

    drawn = cv2.rectangle(CvImg, (StartChord[0], StartChord[1]), (StartChord[0] + width, StartChord[1] - height), (150, 150, 150), thickness=2)

    cv2.imwrite("test.jpg", drawn)

    xNorm = (StartChord[0] + (width / 2)) / Shape[0]                 #Change the image to trainable yolo values
    yNorm = (StartChord[1] - (height / 2)) / Shape[1]

    widthNorm = width / Shape[0]
    heightNorm = height / Shape[1]

    txt = name[:-4]   #remove the.jpg from the name
    txt += ".txt"

    if xNorm > 0 and yNorm > 0 and  widthNorm > 0 and heightNorm > 0:         #Does a simple check to make sure values are valid
        makeLabelFile(txt, xNorm, yNorm, widthNorm, heightNorm)
        return True
    else: 
        return False


 #   drawn = CvImg[StartChord[1], StartChord[0]] = [150, 150, 150]
 #   drawn = CvImg[StartChord[1] - height , StartChord[0] + width] = [150, 150, 150]



def CheckForFalsePostive(im, pix, color):      #make sure pixels around are the same color, if not we can assume a false positive
    try:
        if all((im[pix[0], pix[1] + 2] == color)) and all((im[pix[0], pix[1] - 2] == color)) and all((im[pix[0] + 2, pix[1]] == color)) and all((im[pix[0] - 2, pix[1]] == color)):
            return True
    except IndexError:  
        print("Index out of bounds detected at " + str(pix))
    print("False Positive detected at " + str(pix))
    return False


def findHeight(CvImg, width, height):
    objectHeight = 0
    topFound = False
    bottomFound = False
    objectFound = False
    runtop = [height - 1, width - 1]
    runbottom = [0, 0]

    lastValue = 0

    while runtop != runbottom and not objectFound:                          #Calculate the height of the object and the center of the object
        if (CvImg[runtop[0], runtop[1]] != (50, 50, 50)).any() and not topFound:                                  #Find the top and bottom by detecting where the orange is                             
            if  runtop[1]  > 0:                                                                       
                runtop[1] -= 1
            else:
                runtop[1] = width - 1
                runtop[0] -= 1
        else:
            topFound = CheckForFalsePostive(CvImg, runtop, (50,50,50))
        if (CvImg[runbottom[0], runbottom[1]] != (100,100,150)).any() and not bottomFound:                    #runs when ANY of the pixel colors are not equal
            if  runbottom[1] < width - 1:
                runbottom[1] += 1
            else:
                runbottom[1] = 0
                runbottom[0] += 1
        else:
            bottomFound = CheckForFalsePostive(CvImg, runbottom, (100,100,150))

        if (CvImg[runtop[0], runtop[1]] == (50,50,50)).all() and (CvImg[runbottom[0], runbottom[1]] == (100,100,150)).all():
            objectFound = True        
        if (CvImg[runtop[1], runtop[0]] != (lastValue)).any():
            print(str(CvImg[runtop[1], runtop[0]]))
        lastValue = CvImg[runtop[1], runtop[0]]

    objectHeight = runtop[0] - runbottom[0]
    print("The object height is " + str(objectHeight))    
    return objectHeight  + 5

def findWidth(CvImg, width, height):
    objectWidth = 0
    objectFound = False
    foundLeft = False
    foundRight = False
    runleft = [height - 1, width - 1]                                            #Run right will also be used to find the "Start" of an object
    runright = [0, 0]

    lastValue = 0

    while runleft != runright and not objectFound:                         
        if (CvImg[runright[0], runright[1]] != (50,50,50)).any() and not foundRight:                                  #Find the top and bottom by detecting where the orange is                             
            if  runright[0] < height - 1:                                             # Needs more debugging as a fault orange can throw things off                                
                runright[0] += 1
            else:
                runright[0] = 0
                runright[1] += 1
        else:
            foundLeft = CheckForFalsePostive(CvImg, runright, (50,50,50))

        if (CvImg[runleft[0], runleft[1]] != (50,50,50)).any() and not foundLeft:                    #runs when ANY of the pixel colors are not equal
            if  runleft[0] > 0:
                runleft[0] -= 1
            else:
                runleft[0] = height - 1
                runleft[1] -= 1
        else:
            foundRight = CheckForFalsePostive(CvImg, runright, (50,50,50))

        #    print("Good Index found")
        if (CvImg[runright[0], runright[1]] == (50,50,50)).all() and (CvImg[runleft[0], runleft[1]] == (50,50,50)).all():
            objectFound = True
    objectWidth = runleft[1] - runright[1]
    centerWidth = runleft[0] + runright[0] / 2
    print("Object width is "+ str(objectWidth))
    return [objectWidth + 20, [runright[1] - 10, runright[0]+ 10]]  #Rewrite the runright object to be x,y instead of y,x



def process(input_dir, output_dir):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all jpg images in the input directory
    for image_name in os.listdir(input_dir):
        if image_name.endswith(".jpg"):
            image_path = os.path.join(input_dir, image_name)
            print(f"Processing {image_name}...")
            processed_image = imagePreprocessing(image_path)
            findRequiredCords(processed_image)
            # Save the processed image to the output directory
            output_path = os.path.join(output_dir, f"labeled_{image_name}")
            cv2.imwrite(output_path, processed_image)

def empty_directory(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)  
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  
    print(f"All items in {directory} have been removed.")


def run(pal, location):
    empty_directory('labels')
    empty_directory('subject')
    for pic_name in os.listdir(location):
        findRequiredCords(imagePreproccessing(pal, os.path.join(location, pic_name)), pic_name)

run([
        150, 100, 100,     # Orange
        50, 50, 50,      # Cone Black  (This color is located on the bottom of the cone)
        0, 0, 0,         # Normal Black
        110, 110, 110,   # 
        200, 200, 200,
        164, 135, 80,
        0, 0, 255,
        0, 255, 0, 
    ] , '/home/jas/Downloads/png2jpg')