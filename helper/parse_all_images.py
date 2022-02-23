import glob
import random


def get_all_image(imdir = "helper/images/"):

    title = []

    for image in glob.glob(imdir + '*.jpg'):

        title.append(image.replace('helper/images\\',''))
    return random.choice(title)

