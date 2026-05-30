from PIL import Image
import numpy as np
import os
import sys

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

def knn_euclidean_api(target_rgb, dataset_rgb):
    target_2d = target_rgb.reshape(-1, 3)
    combine = target_2d[:, np.newaxis, :] - dataset_rgb[np.newaxis, :, :]
    distances = np.sqrt(np.sum(combine**2, axis=2))
    nearest_2d = np.argmin(distances, axis=1)
    return nearest_2d.reshape(target_rgb.shape[:2])

FOLDER_CATEGORY = {
    "building": "assets/Building",
    "cloud":    "assets/Cloud",
    "nature":   "assets/Nature",
    "vehicle":  "assets/Vehicle",
}

def run_mosaic(target_path, category, output_path, grid_m=64, grid_n=64):
    folder = FOLDER_CATEGORY.get(category.lower())
    if folder is None:
        raise ValueError(f"kategori tidak diketahui: {category}. Kategori: {list(FOLDER_CATEGORY.keys())}")

    cache_path = os.path.join("cache", f"{category}_avg.npz")

    if os.path.exists(cache_path):
        print(f"1/4 ambil cache dari {cache_path}")
        data = np.load(cache_path, allow_pickle=True)
        avg_rgb = data['avg_rgb']
        img_paths = list(data['paths'])
    else:
        print(f"1/4 ambil dataset dari {folder}")
        avg_rgb, img_paths = get_folder_avg_rgb(folder)
        np.savez(cache_path, avg_rgb=avg_rgb, paths=np.array(img_paths))
        print(f"      Cache disimpan ke {cache_path}")

    print(f"2/4 menghitung avg RGB per grid dari {target_path}")
    avg_color_pixel, width, height, grid_w, grid_h = get_avg_rgb_per_grid(target_path, grid_m, grid_n)

    print(f"3/4 KNN matching ({grid_m}x{grid_n} grid, {len(img_paths)} tiles)")
    nearest = knn_euclidean_api(avg_color_pixel, avg_rgb)

    print(f"4/4 Menyusun mosaic: {output_path}")
    result = mosaic(nearest, img_paths, width, height, grid_w, grid_h)
    result.save(output_path)
    print("selesai")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("penggunaan: python main.py <target_image> <category> <output_path>")
        print("       category: building | cloud | nature | vehicle")
        sys.exit(1)

    run_mosaic(sys.argv[1], sys.argv[2], sys.argv[3])