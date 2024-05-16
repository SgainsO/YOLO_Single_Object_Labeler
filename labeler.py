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
    
 #   cone = cone.resize(Shape)

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

    print("The start chord is:" + str(StartChord))
    drawn = cv2.rectangle(CvImg, (StartChord[0], StartChord[1]), (StartChord[0] + width, StartChord[1] - height), (250, 250, 250), thickness=6)

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



#def CheckForFalsePostive(im, pix, color, size):      #make sure pixels around are the same color, if not we can assume a false positive
#    tolerance = 50
#    if pix[1] + tolerance > size[1]:
#        if all((im[pix[0], pix[1] - tolerance] == color)) and all((im[pix[0] + tolerance, pix[1]] == color)) and all((im[pix[0] - tolerance, pix[1]] == color)):
#            return True
#
#    if pix[0] + 50 > size[0]:
#        if all((im[pix[0], pix[1] + tolerance] == color)) and all((im[pix[0], pix[1] - tolerance] == color)) and all((im[pix[0] + tolerance, pix[1]] == color)) and all((im[pix[0] - tolerance, pix[1]] == color)):
#            return True
#    
#    
#    try:
#        if all((im[pix[0], pix[1] + tolerance] == color)) and all((im[pix[0], pix[1] - tolerance] == color)) and all((im[pix[0] + tolerance, pix[1]] == color)) and all((im[pix[0] - tolerance, pix[1]] == color)):
#            return True
#    except IndexError:  
#        pass
#    return False
def CheckForFalsePostive(im, pix, color, size):
    toleranceX = int(size[1] * .075)  # Assuming im is a NumPy array or similar, adjust accordingly if it's not
    toleranceY = int(size[0] * .04)
    # Check if the indices are within the bounds after adding/subtracting tolerance
    
    checks = [
        (pix[0], pix[1] + 3),          #Pix 0 is Y 
        (pix[0], pix[1] - 3),
        (pix[0] + 3, pix[1]),
        (pix[0] - 3, pix[1])
    ]

    for y, x in checks:
        if 0 <= x < size[1] and 0 <= y < size[0]:
            if (im[y,x] != color).any():  
            #    print("return false")
                return False
    return True







def findHeight(CvImg, width, height, topColor, bottomColor):
    objectHeight = 0
    topFound = False
    bottomFound = False
    objectFound = False
    runtop = [height - 1, width - 1]
    runbottom = [0, 0]
    
    try: 
        while runtop != runbottom and not objectFound:                          #Calculate the height of the object and the center of the object
            if (CvImg[runtop[0], runtop[1]] != bottomColor).any():                                  #Find the top and bottom by detecting where the orange is                             
                if  runtop[1]  > 0:                                                                       
                    runtop[1] -= 1
                else:
                    runtop[1] = width - 1
                    runtop[0] -= 1
            elif (CvImg[runtop[0], runtop[1]] == bottomColor).any() and not topFound:
                topFound = CheckForFalsePostive(CvImg, runtop, bottomColor, [height - 1, width -1])
                if topFound == False:
                    if  runtop[1]  > 0:                                                                       
                        runtop[1] -= 1
                    else:
                        runtop[1] = width - 1
                        runtop[0] -= 1


            if (CvImg[runbottom[0], runbottom[1]] != topColor).any():                    #runs when ANY of the pixel colors are not equal
                if  runbottom[1] < width - 1:
                    runbottom[1] += 1
                else:
                    runbottom[1] = 0
                    runbottom[0] += 1
            elif (CvImg[runbottom[0], runbottom[1]] == topColor).any() and not bottomFound:
                bottomFound = CheckForFalsePostive(CvImg, runbottom, topColor, [height - 1, width -1])
                if bottomFound == False:
                    if  runbottom[1] < width - 1:
                        runbottom[1] += 1
                    else:
                        runbottom[1] = 0
                        runbottom[0] += 1
 #           if (CvImg[runtop[0], runtop[1]] == bottomColor).all() and (CvImg[runbottom[0], runbottom[1]] == topColor).all():
 #               objectFound = True  
            if topFound and bottomFound:
                objectFound = True    
    except:
        print("Could not find color in image")
    objectHeight = runtop[0] - runbottom[0]
    print("The object height is " + str(objectHeight))

    if height > objectHeight + (height * .04):    
        return objectHeight  + int((height * .04))
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
    try: 
        while runleft != runright and not objectFound:                         
            if (CvImg[runright[0], runright[1]] != leftColor).any():                                  #Find the top and bottom by detecting where the orange is                             
                if  runright[0] < height - 1:                                             # Needs more debugging as a fault orange can throw things off                                
                    runright[0] += 1
                else:
                    runright[0] = 0
                    runright[1] += 1
            elif (CvImg[runright[0], runright[1]] == leftColor).any() and not foundRight:
                foundRight = CheckForFalsePostive(CvImg, runright, leftColor, [height - 1, width -1])
                if foundRight == False:
                    if  runright[0] < height - 1:                                             # Needs more debugging as a fault orange can throw things off                                
                        runright[0] += 1
                    else:
                        runright[0] = 0
                        runright[1] += 1
            if (CvImg[runleft[0], runleft[1]] != rightColor).any() and not foundLeft:                    #runs when ANY of the pixel colors are not equal
                if  runleft[0] > 0:
                    runleft[0] -= 1
                else:
                    runleft[0] = height - 1
                    runleft[1] -= 1
            else:
                foundLeft = CheckForFalsePostive(CvImg, runright, rightColor, [height - 1, width -1])
                if foundLeft == False:
                    if  runleft[0] > 0:
                        runleft[0] -= 1
                    else:
                        runleft[0] = height - 1
                        runleft[1] -= 1

            #    print("Good Index found")
 #           if (CvImg[runright[0], runright[1]] == rightColor).all() and (CvImg[runleft[0], runleft[1]] == leftColor).all():
 #               print(str(CvImg[runright[0], runright[1]]) + " " + str(CvImg[runleft[0], runleft[1]]))
 #               objectFound = True
            if foundLeft and foundRight:
                print(str(CvImg[runright[0], runright[1]]) + " " + str(CvImg[runleft[0], runleft[1]]))
                objectFound = True
    except:
        print("Could not find color in image")
    objectWidth = runleft[1] - runright[1]
    centerWidth = runleft[0] + runright[0] / 2
    print("Object width is "+ str(objectWidth))
    if width > objectWidth + (width * .082) and height > runright[1] + (height * .04) and runright[1] - (width * .04) >= 0:
        return [objectWidth + int((width * .082)), [runright[1] - int((width * .04)), runright[0] + int((height *.04))]]  #Rewrite the runright object to be x,y instead of y,x
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