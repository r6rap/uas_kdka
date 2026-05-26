from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os

m = 64
n = 64

folder = "Building"

r, g, b = 0.0, 0.0, 0.0

for file in os.listdir(folder):
    img_path = os.path.join(folder, file)

    try:
        with Image.open(img_path) as img:
            img_rgb = img.convert('RGB')

            img_array = np.array(img_rgb)

            avg_r, avg_g, avg_b = np.mean(img_array, axis=(0, 1))

            print(
                f"{file}: "
                f"({avg_r:.2f}, {avg_g:.2f}, {avg_b:.2f})"
            )

    except Exception as e:
        print(f"failed: {file} = {e}")

avg_color_pixel = np.zeros((n, m, 3))

img = Image.open('target_image.jpeg')

width, height = img.size

grid_w = width // m
grid_h = height // n

img_array = np.array(img)

plt.figure(figsize=(10, 10))
plt.imshow(img_array)

for x in range(0, width, grid_w):
    plt.axvline(x=x, color='red', linewidth=0.3)

for y in range(0, height, grid_h):
    plt.axhline(y=y, color='red', linewidth=0.3)

for row in range(n):

    for col in range(m):

        x1 = col * grid_w
        x2 = x1 + grid_w

        y1 = row * grid_h
        y2 = y1 + grid_h

        tile = img_array[y1:y2, x1:x2]

        avg_rgb = tile.mean(axis=(0, 1))

        avg_color_pixel[row, col] = avg_rgb

print(avg_color_pixel.shape)

plt.title(f"{m} x {n} Grid")
plt.ylim(height, 0)
plt.show()

preview = avg_color_pixel.astype(np.uint8)

plt.figure(figsize=(10, 10))
plt.imshow(preview, interpolation='nearest')
plt.title("pixel")
plt.show()