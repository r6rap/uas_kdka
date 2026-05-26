from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

m = 64
n = 64

# buat array kosong untuk menyimpan warna rata-rata tiap grid (64x64, tiap elemen punya RGB)
avg_color_pixel = np.zeros((n, m, 3))

# buka gambar
img = Image.open('target_image.jpeg')

# ambil ukuran gambar asli
width, height = img.size

# hitung ukuran tiap grid (pixel)
grid_w = width // m
grid_h = height // n

# ubah object PIL menjadi numpy array agar bisa diproses seperti matrix
img_array = np.array(img)

# tampilkan gambar asli
plt.figure(figsize=(10, 10))
plt.imshow(img_array)

# gambar garis vertikal untuk membagi kolom grid
for x in range(0, width, grid_w):
    plt.axvline(x=x, color='red', linewidth=0.3)

# gambar garis horizontal untuk membagi baris grid
for y in range(0, height, grid_h):
    plt.axhline(y=y, color='red', linewidth=0.3)

# loop semua baris grid
for row in range(n):

    # loop semua kolom grid
    for col in range(m):

        # tentukan batas kiri-kanan tile
        x1 = col * grid_w
        x2 = x1 + grid_w

        # tentukan batas atas-bawah tile
        y1 = row * grid_h
        y2 = y1 + grid_h

        # ambil potongan gambar sesuai tile
        tile = img_array[y1:y2, x1:x2]

        # hitung rata-rata RGB tile
        avg_rgb = tile.mean(axis=(0, 1))

        # simpan warna rata-rata ke array output
        avg_color_pixel[row, col] = avg_rgb

print(avg_color_pixel.shape)

plt.title(f"{m} x {n} Grid")
plt.ylim(height, 0)
plt.show()

# ubah float ke uint8 agar valid sebagai gambar
preview = avg_color_pixel.astype(np.uint8)

# tampilkan hasil pixelated image
plt.figure(figsize=(10, 10))
plt.imshow(preview, interpolation='nearest')
plt.title("pixel")
plt.show()