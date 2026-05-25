from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt

m = 64
n = 64

avg_color_pixel = np.zeros((n, m, 3))

img = Image.open('target_image.jpeg')
width, height = img.size

grid_w = width // m
grid_h = height // n

# ?
img_array = np.array(img)

#?
plt.figure(figsize=(10, 10))
plt.imshow(img_array)

# vertical ?
for x in range(0, width, grid_w):
    plt.axvline(x=x, color='red', linewidth=0.3)

# horizontal ?
for y in range(0, height, grid_h):
    plt.axhline(y=y, color='red', linewidth=0.3)

# ?
for row in range(n):
    for col in range(m):

        x1 = col * grid_w
        x2 = x1 + grid_w

        y1 = row * grid_h
        y2 = y1 + grid_h

        tile = img_array[y1:y2, x1:x2]

        avg_rgb = tile.mean(axis=(0,1))

        avg_color_pixel[row, col] = avg_rgb

print(avg_color_pixel)
print(height, width)
print(grid_h, grid_w)

plt.title(f"{m} x {n} Grid")
plt.xlim(0, width)
plt.ylim(height, 0)
plt.show()

preview = avg_color_pixel.astype(np.uint8)
plt.imshow(preview)
plt.title("average rgb per pixel")
plt.show()