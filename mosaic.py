from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt

def average_color(image):
    img = np.asarray(image)
    return img.mean(axis=(0, 1))

def load_images_from_folder(folder, tile_size):
    tiles = []
    colors = []

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        try:
            img = Image.open(path).convert('RGB')
            img = img.resize(tile_size, Image.Resampling.LANCZOS)
            tiles.append(img)
            colors.append(average_color(img))
        except Exception as e:
            print(f"failed loading file {file}: {e}")

    return tiles, colors

def find_best_match(target_color, tile_colors):
    distances = np.linalg.norm(tile_colors - target_color, axis=1)
    return np.argmin(distances)

def create_mosaic(target_image, tiles, tile_colors, grid_size):
    W, H = target_image.size
    M, N = grid_size

    tile_w, tile_h = W // M, H // N
    mosaic = Image.new("RGB", (W, H))

    for i in range(M):
        for j in range(N):
            box = (i * tile_w, j * tile_h,
                   (i + 1) * tile_w, (j + 1) * tile_h)

            tile = target_image.crop(box)
            target_color = average_color(tile)
            best_idx = find_best_match(target_color, tile_colors)

            mosaic.paste(tiles[best_idx], box)

    return mosaic

target_image = Image.open('target_image_2.jpeg').convert('RGB')

tile_folder = "Mountain"

M = 100
N = 100
grid_size = (M, N)

tile_w = target_image.size[0] // M
tile_h = target_image.size[1] // N

tiles, tile_colors = load_images_from_folder(tile_folder, (tile_w, tile_h))

if not tiles:
    raise ValueError("No tile images were successfully loaded from the Forest folder.")

mosaic = create_mosaic(target_image, tiles, tile_colors, grid_size)
plt.figure(figsize=(10, 10))
plt.imshow(mosaic)
plt.axis("off")

mosaic.save("photomosaic_output.jpg")
print("Photomosaic saved as photomosaic_output_2.jpg")