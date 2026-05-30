# Photomosaic API

Backend service untuk generate photomosaic dari gambar target. Dibangun dengan Go (Gin) + Python (PIL, NumPy).

**Base URL:** `http://localhost:8080`

---

## Endpoints

### `GET /categories`

Mengambil daftar kategori tile yang tersedia.

**Request**

Tidak memerlukan body atau parameter apapun.

**Response `200 OK`**

```json
{
  "categories": ["building", "cloud", "nature", "vehicle"]
}
```

**Contoh**

```bash
curl http://localhost:8080/categories
```

---

### `POST /mosaic`

Mengupload gambar target dan memulai proses generate photomosaic secara async. Request langsung return `job_id` tanpa menunggu proses selesai.

**Request**

Content-Type: `multipart/form-data`

| Field      | Tipe   | Wajib | Keterangan                                          |
|------------|--------|-------|-----------------------------------------------------|
| `image`    | file   | ✓     | Gambar target. Format: JPG, PNG                     |
| `category` | string | ✓     | Kategori tile. Nilai: `building`, `cloud`, `nature`, `vehicle` |

**Response `202 Accepted`**

```json
{
  "job_id": "1780175716281397200",
  "status": "pending"
}
```

**Response `400 Bad Request`**

```json
{
  "error": "category is required"
}
```

```json
{
  "error": "invalid category: forest"
}
```

```json
{
  "error": "image file is required"
}
```

**Contoh**

```bash
curl -X POST http://localhost:8080/mosaic \
  -F "image=@foto.jpg" \
  -F "category=building"
```

---

### `GET /status/:id`

Mengecek status job. Jika job sudah selesai (`done`), response langsung berupa file gambar binary (bukan JSON).

**Path Parameter**

| Parameter | Keterangan                           |
|-----------|--------------------------------------|
| `id`      | `job_id` yang didapat dari `POST /mosaic` |

**Response — Job belum selesai `200 OK`**

```json
{
  "job_id": "1780175716281397200",
  "status": "processing"
}
```

**Response — Job selesai `200 OK`**

Binary image (`image/jpeg`). Bukan JSON.

**Response — Job gagal `200 OK`**

```json
{
  "job_id": "1780175716281397200",
  "status": "failed",
  "error": "exit status 1: ..."
}
```

**Response — Job tidak ditemukan `404 Not Found`**

```json
{
  "error": "job not found"
}
```

**Contoh — simpan hasil ke file**

```bash
curl http://localhost:8080/status/1780175716281397200 --output result.jpg
```

---

## Alur Penggunaan

```
1. GET  /categories          → ambil daftar kategori

2. POST /mosaic              → upload gambar + kategori
                               → dapat job_id

3. GET  /status/:id          → polling setiap 2-3 detik
   └── status: pending       → belum mulai
   └── status: processing    → Python sedang berjalan
   └── status: failed        → lihat field "error"
   └── content-type: image/  → selesai, tampilkan gambar
```

---

## Catatan untuk Frontend

**Polling interval:** Gunakan minimal 2 detik. Proses mosaic 64×64 grid dengan 400 tile memakan waktu 5–30 detik tergantung spesifikasi mesin.

**Deteksi response done:** Jangan andalkan field JSON `status: "done"` — cek `Content-Type` header dari response. Kalau `image/jpeg`, langsung render sebagai gambar.

**Job ID tidak persisten:** Job store ada di memory. Jika server di-restart, semua job hilang. Jangan simpan `job_id` lintas sesi.

---

## Menjalankan Server

**Syarat**

- Go 1.21+
- Python 3.9+ dengan dependensi: `pip install Pillow numpy`
- Dataset tile tersedia di folder `assets/`

**Jalankan**

```bash
go run main.go
```

Server running on `http://localhost:8080`.