from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt

m = 32
n = 32

img = Image.open('target_image_2.jpeg')
width, height = img.size

tile_w = width / m
tile_h = height / n

print(f"Tile size: {tile_w}x{tile_h}")