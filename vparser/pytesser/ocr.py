from __future__ import print_function
import sys
from pytesser import *
from PIL import ImageOps, ImageEnhance

def myEqualize(im):
    im=im.convert('L')
    contr = ImageEnhance.Contrast(im)
    im = contr.enhance(0.3)
    bright = ImageEnhance.Brightness(im)
    #im = bright.enhance(2)
    #im.show()
    return im

if __name__ == "__main__":
    if len(sys.argv)>1:
        filename = sys.argv[1]
        image = Image.open(filename)
        if '-e' in sys.argv:
            image = ImageOps.equalize(image)
        if '-m' in sys.argv:
            image = myEqualize(image)
        if '-b' in sys.argv:
            image = image.convert('1')
        print(image_to_string(image).strip())
    else:
        print("Enter valid image filename")
        exit(0)