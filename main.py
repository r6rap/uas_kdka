from PIL import Image
import numpy as np
import os

m = 64
n = 64

def get_folder_avg_rgb(folder):

    avg_rgb = []
    img_paths = []

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)

        if not os.path.isfile(file_path):
            continue

        try:
            with Image.open(file_path) as img:

                img_rgb = img.convert("RGB")

                img_array = np.array(img_rgb)

                avg_r, avg_g, avg_b = np.mean(img_array, axis=(0, 1))

                avg_rgb.append((avg_r, avg_g, avg_b))
                img_paths.append(file_path)

        except Exception as e:
            print(f"failed: {file} = {e}")

    return np.array(avg_rgb), img_paths

def get_avg_rgb_per_grid(image_path, m, n):

    img = Image.open(image_path).convert("RGB")

    width, height = img.size

    grid_w = width / m
    grid_h = height / n

    img_array = np.array(img)

    avg_color_pixel = np.zeros((n, m, 3))

    for row in range(n):

        for col in range(m):

            x1 = int(col * grid_w)
            x2 = int((col + 1) * grid_w)

            y1 = int(row * grid_h)
            y2 = int((row + 1) * grid_h)

            tile = img_array[y1:y2, x1:x2]

            avg_rgb = tile.mean(axis=(0, 1))

            avg_color_pixel[row, col] = avg_rgb

    return avg_color_pixel, width, height, grid_w, grid_h

def knn_euclidean(target_rgb, dataset_rgb):

    rows, cols, _ = target_rgb.shape

    nearest = np.zeros((rows, cols), dtype=int)

    for row in range(rows):

        for col in range(cols):

            target_r, target_g, target_b = target_rgb[row, col]

            min_distance = float('inf')
            best_neighbor = -1

            for i in range(len(dataset_rgb)):

                dataset_r, dataset_g, dataset_b = dataset_rgb[i]

                distance = np.sqrt((target_r - dataset_r) ** 2 + (target_g - dataset_g) ** 2 + (target_b - dataset_b) ** 2)

                if distance < min_distance:
                    min_distance = distance
                    best_neighbor = i

            nearest[row, col] = best_neighbor

    return nearest

def mosaic(nearest, img_path, target_width, target_height, grid_w, grid_h):

    tiles = []
    for path in img_path:
        img = Image.open(path).convert("RGB")
        tiles.append(img)

    rows, cols = nearest.shape

    mosaic = Image.new("RGB", (target_width, target_height))

    for row in range(rows):
        for col in range(cols):

            nearest_index = nearest[row, col]

            tile = tiles[nearest_index]

            tile = tile.resize((int(grid_w), int(grid_h)))

            x = col * grid_w
            y = row * grid_h

            mosaic.paste(tile, (int(x), int(y)))

    return mosaic




avg_building, path_building = get_folder_avg_rgb("Building")
avg_color_pixel, width, height, grid_w, grid_h = get_avg_rgb_per_grid("target_image.jpeg", m, n)
nearest = knn_euclidean(avg_color_pixel, avg_building)
print(nearest[0, 1])
print(path_building[7])
print("width: ",width, "height: ", height)
print("grid_w: ", grid_w, "grid_h: ", grid_h)
print("grid w * m: ", grid_w * m, "grid_h * n: ", grid_h * n)
outputMosaic = mosaic(nearest, path_building, width, height, grid_w, grid_h)
outputMosaic.save("result.jpg")