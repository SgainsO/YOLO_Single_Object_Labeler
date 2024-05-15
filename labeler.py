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
    
#    cone = cone.resize(Shape)

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



def findRequiredCords(CvImg, name, top, bottom, left, right):
  #  cv2.imshow("test", CvImg)
  #  cv2.waitKey(0)
  #  cv2.destroyAllWindows()
    
    imageHeight, imageWidth, channels = CvImg.shape
    height = findHeight(CvImg, imageWidth, imageHeight, top, bottom)
    width, StartChord = findWidth(CvImg, imageWidth, imageHeight, left, right)


    os.chdir("subject")
    cv2.imwrite(f"dil_{name}", drawn)
    os.chdir("..")

    xNorm = (StartChord[0] + (width / 2)) / imageWidth                 #Change the image to trainable yolo values
    yNorm = (StartChord[1] - (height / 2)) / imageHeight

    widthNorm = width / imageWidth
    heightNorm = height / imageHeight

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
        pass
    return False


def findHeight(CvImg, width, height, topColor, bottomColor):
    objectHeight = 0
    topFound = False
    bottomFound = False
    objectFound = False
    runtop = [height - 1, width - 1]
    runbottom = [0, 0]


    while runtop != runbottom and not objectFound:                          #Calculate the height of the object and the center of the object
        if (CvImg[runtop[0], runtop[1]] != bottomColor).any() and not topFound:                                  #Find the top and bottom by detecting where the orange is                             
            if  runtop[1]  > 0:                                                                       
                runtop[1] -= 1
            else:
                runtop[1] = width - 1
                runtop[0] -= 1
        else:
            topFound = CheckForFalsePostive(CvImg, runtop, bottomColor)
        if (CvImg[runbottom[0], runbottom[1]] != topColor).any() and not bottomFound:                    #runs when ANY of the pixel colors are not equal
            if  runbottom[1] < width - 1:
                runbottom[1] += 1
            else:
                runbottom[1] = 0
                runbottom[0] += 1
        else:
            bottomFound = CheckForFalsePostive(CvImg, runbottom, topColor)

        if (CvImg[runtop[0], runtop[1]] == bottomColor).all() and (CvImg[runbottom[0], runbottom[1]] == topColor).all():
            objectFound = True        

    objectHeight = runtop[0] - runbottom[0]
    print("The object height is " + str(objectHeight))

    if height > objectHeight + (height * .02):    
        return objectHeight  + int((height * .02))
    else:
        return objectHeight

def findWidth(CvImg, width, height, leftColor, rightColor):
    objectWidth = 0
    objectFound = False
    foundLeft = False
    foundRight = False
    runleft = [height - 1, width - 1]                                            #Run right will also be used to find the "Start" of an object
    runright = [0, 0]

    lastValue = 0

    while runleft != runright and not objectFound:                         
        if (CvImg[runright[0], runright[1]] != leftColor).any() and not foundRight:                                  #Find the top and bottom by detecting where the orange is                             
            if  runright[0] < height - 1:                                             # Needs more debugging as a fault orange can throw things off                                
                runright[0] += 1
            else:
                runright[0] = 0
                runright[1] += 1
        else:
            foundLeft = CheckForFalsePostive(CvImg, runright, leftColor)

        if (CvImg[runleft[0], runleft[1]] != rightColor).any() and not foundLeft:                    #runs when ANY of the pixel colors are not equal
            if  runleft[0] > 0:
                runleft[0] -= 1
            else:
                runleft[0] = height - 1
                runleft[1] -= 1
        else:
            foundRight = CheckForFalsePostive(CvImg, runright, rightColor)

        #    print("Good Index found")
        if (CvImg[runright[0], runright[1]] == rightColor).all() and (CvImg[runleft[0], runleft[1]] == leftColor).all():
            objectFound = True

    objectWidth = runleft[1] - runright[1]
    centerWidth = runleft[0] + runright[0] / 2
    print("Object width is "+ str(objectWidth))
    if width > objectWidth + (width * .075) and height > runright[1] + (height * .04) and runright[1] - (width * .04) >= 0:
        return [objectWidth + int((width * .075)), [runright[1] - int((width * .04)), runright[0] + int((height *.04))]]  #Rewrite the runright object to be x,y instead of y,x
    else:                                                                                                  #Try to extend the borders of the width and height of the object
        return [objectWidth , [runright[1], runright[0]]]  #Rewrite the runright object to be x,y instead of y,x


def empty_directory(directory):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)  
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)  
    print(f"All items in {directory} have been removed.")


def run(pal, location, top, bottom, left, right):
    empty_directory('labels')
    empty_directory('subject')
    FailedLabelList = []
    for pic_name in os.listdir(location):
        labelMade = findRequiredCords(imagePreproccessing(pal, os.path.join(location, pic_name)), pic_name, top, bottom, left, right)
        if not labelMade:
            FailedLabelList.append(pic_name)
    print("The following images ran into errors and were thus not labeled:")
    for item in FailedLabelList:
        print(item)
    print("Please use your original images to make your training dataset")
    print("The images in subjects should be used to ensure that the labels are accurate")