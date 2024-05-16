import labeler

###CURRENTY NONFUNCTIONAL

### These will be colors the image will be changed into
### This is so it will be easy to identify the colors of the certain pixels
### Greater variaty means a greater probability that a subject will be identified
palette =  [
        150, 100, 100,     # Orange
        50, 50, 50,        # Black  To Identify
        0, 0, 0,         
        110, 110, 110,    
        200, 200, 200,
        164, 135, 80,
        0, 0, 255,
        0, 255, 0, 
    ]


###Link to a folder that ONLY chontains .jpg images! (no pngs)
linkToFolder = '/home/jas/Downloads/png2jpg'


### These are the expects colors of the top, bottom, left and right
### These colors must be included in the palette
### NOTICE HOW THE COLOR IS FLIPPED
topPixel = (100, 100, 150)

bottomPixel = (50, 50, 50)

leftPixel = (50, 50, 50)

rightPixel = (50, 50, 50)


labeler.run(palette, linkToFolder,
             topPixel, bottomPixel, leftPixel, rightPixel, )