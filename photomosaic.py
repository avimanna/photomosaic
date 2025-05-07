import os, random, argparse
from PIL import Image
import imghdr
import numpy as np

def getAverageRGB(image):
    im = np.array(image)
    w, h, d = im.shape
    return tuple(np.average(im.reshape(w*h, d), axis=0))

def splitImage(image, size):
    W, H = image.size
    m, n = size
    w, h = int(W/n), int(H/m)
    imgs = [image.crop((i*w, j*h, (i+1)*w, (j+1)*h)) for j in range(m) for i in range(n)]
    return imgs

def getImages(imageDir):
    files = os.listdir(imageDir)
    images = []
    for file in files:
        filePath = os.path.abspath(os.path.join(imageDir, file))
        try:
            with open(filePath, "rb") as fp:
                im = Image.open(fp)
                images.append(im)
                im.load()
        except:
            print(f"Invalid image: {filePath}")
    return images

def getImageFilenames(imageDir):
    files = os.listdir(imageDir)
    filenames = []
    for file in files:
        filePath = os.path.abspath(os.path.join(imageDir, file))
        try:
            if imghdr.what(filePath):
                filenames.append(filePath)
        except:
            print(f"Invalid image: {filePath}")
    return filenames

def getBestMatchIndex(input_avg, avgs):
    min_index, min_dist = 0, float("inf")
    for index, val in enumerate(avgs):
        dist = sum((val[i] - input_avg[i])**2 for i in range(3))
        if dist < min_dist:
            min_dist, min_index = dist, index
    return min_index

def createImageGrid(images, dims):
    m, n = dims
    width, height = max(img.size[0] for img in images), max(img.size[1] for img in images)
    grid_img = Image.new('RGB', (n*width, m*height))
    for index, img in enumerate(images):
        row, col = divmod(index, n)
        grid_img.paste(img, (col*width, row*height))
    return grid_img

def createPhotomosaic(target_image, input_images, grid_size, reuse_images=True):
    target_images = splitImage(target_image, grid_size)
    avgs = [getAverageRGB(img) for img in input_images]
    output_images = [input_images[getBestMatchIndex(getAverageRGB(img), avgs)] for img in target_images]
    return createImageGrid(output_images, grid_size)

def main():
    parser = argparse.ArgumentParser(description='Creates a photomosaic from input images')
    parser.add_argument('--target-image', dest='target_image', required=True)
    parser.add_argument('--input-folder', dest='input_folder', required=True)
    parser.add_argument('--grid-size', nargs=2, dest='grid_size', required=True)
    parser.add_argument('--output-file', dest='outfile', required=False)
    args = parser.parse_args()

    target_image = Image.open(args.target_image)
    input_images = getImages(args.input_folder)
    if not input_images:
        print(f'No input images found in {args.input_folder}. Exiting.')
        exit()

    random.shuffle(input_images)
    grid_size = (int(args.grid_size[0]), int(args.grid_size[1]))
    output_filename = args.outfile if args.outfile else 'mosaic.png'
    reuse_images, resize_input = True, True

    if not reuse_images and grid_size[0] * grid_size[1] > len(input_images):
        print('Grid size exceeds number of images')
        exit()

    if resize_input:
        dims = (target_image.size[0] // grid_size[1], target_image.size[1] // grid_size[0])
        for img in input_images:
            img.thumbnail(dims)

    mosaic_image = createPhotomosaic(target_image, input_images, grid_size, reuse_images)
    mosaic_image.save(output_filename, 'PNG')
    print(f"Saved output to {output_filename}")

if __name__ == '__main__':
    main()
