from PIL import Image
import numpy as np
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    f1_score, precision_score, recall_score, confusion_matrix
)

m = 64
n = 64

def get_folder_avg_rgb(folder):
    avg_rgb, img_paths = [], []
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if not os.path.isfile(file_path):
            continue
        try:
            with Image.open(file_path) as img:
                img_array = np.array(img.convert("RGB"))
                r, g, b   = np.mean(img_array, axis=(0, 1))
                avg_rgb.append((r, g, b))
                img_paths.append(file_path)
        except Exception as e:
            print(f"Gagal memproses file: {file} - Error: {e}")
    return np.array(avg_rgb), img_paths


def get_avg_rgb_per_grid(image_path, m, n):
    img             = Image.open(image_path).convert("RGB")
    width, height   = img.size
    grid_w, grid_h  = width / m, height / n
    img_array       = np.array(img)
    avg_color_pixel = np.zeros((n, m, 3))
    for row in range(n):
        for col in range(m):
            x1, x2 = int(col * grid_w),       int((col + 1) * grid_w)
            y1, y2 = int(row * grid_h),       int((row + 1) * grid_h)
            avg_color_pixel[row, col] = img_array[y1:y2, x1:x2].mean(axis=(0, 1))
    return avg_color_pixel, width, height, grid_w, grid_h


def mosaic(nearest, img_path, target_width, target_height, grid_w, grid_h):
    tiles      = [Image.open(p).convert("RGB") for p in img_path]
    rows, cols = nearest.shape
    result     = Image.new("RGB", (target_width, target_height))
    for row in range(rows):
        for col in range(cols):
            tile = tiles[nearest[row, col]].resize((int(grid_w), int(grid_h)))
            result.paste(tile, (int(col * grid_w), int(row * grid_h)))
    return result


def train_and_evaluate(avg_rgb, output_dir="output"):
    """
    Tiap tile = 1 sampel dengan fitur [R, G, B] dan label = indeks tile.
    Karena setiap label hanya muncul 1x, kita buat data augmented (dengan
    noise kecil) agar train/test split & cross-validation bisa berjalan.
    """
    os.makedirs(output_dir, exist_ok=True)

    np.random.seed(42)
    n_aug  = 8      # jumlah salinan per tile
    noise  = 5.0    # std noise (skala 0-255)

    rows_list, labels_list = [], []
    for idx, rgb in enumerate(avg_rgb):
        aug = np.clip(rgb + np.random.randn(n_aug, 3) * noise, 0, 255)
        rows_list.append(aug)
        labels_list.extend([idx] * n_aug)
    X_aug = np.vstack(rows_list)          # (N * n_aug, 3)
    y_aug = np.array(labels_list)         # (N * n_aug,)

    df           = pd.DataFrame(X_aug, columns=["R", "G", "B"])
    df["label"]  = y_aug

    X = df[["R", "G", "B"]]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n[GridSearchCV] Mencari hyperparameter terbaik...")
    dtree      = DecisionTreeClassifier(class_weight="balanced")
    param_grid = {
        "max_depth":         [4, 5, 6, 7],
        "min_samples_split": [2, 3, 4],
        "min_samples_leaf":  [1, 2, 3],
        "random_state":      [0, 42],
    }
    cv          = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid_search = GridSearchCV(dtree, param_grid, cv=cv, n_jobs=-1)
    grid_search.fit(X_train, y_train)
    print("Parameter terbaik:", grid_search.best_params_)

    dtree  = grid_search.best_estimator_
    y_pred = dtree.predict(X_test)

    print("\n[Evaluasi Model]")
    print(f"F-1 Score       : {f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"Precision Score : {precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"Recall Score    : {recall_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")

    print("\n[Plot] Membuat feature importance...")
    imp_df = pd.DataFrame({
        "Feature Name": X_train.columns,
        "Importance":   dtree.feature_importances_,
    })
    fi  = imp_df.sort_values(by="Importance", ascending=False)
    fi2 = fi.head(10)

    plt.figure(figsize=(10, 8))
    sns.barplot(data=fi2, x="Importance", y="Feature Name")
    plt.title("Top 10 Feature Importance Each Attributes (Decision Tree)", fontsize=18)
    plt.xlabel("Importance", fontsize=16)
    plt.ylabel("Feature Name", fontsize=16)
    plt.tight_layout()
    path_fi = os.path.join(output_dir, "feature_importance_dtree.png")
    plt.savefig(path_fi, format="png", bbox_inches="tight")
    plt.close()
    print(f"Plot feature importance disimpan di: {path_fi}")

    unique_classes = np.unique(np.concatenate([y_test.values, y_pred]))[:20]
    mask = np.isin(y_test, unique_classes) & np.isin(y_pred, unique_classes)
    cm   = confusion_matrix(y_test[mask], y_pred[mask], labels=unique_classes)

    plt.figure(figsize=(9, 9))
    sns.heatmap(data=cm, linewidths=.5, annot=True, fmt="d", cmap="Blues",
                xticklabels=unique_classes, yticklabels=unique_classes)
    plt.ylabel("Actual label")
    plt.xlabel("Predicted label")
    acc_title = "Accuracy Score for Decision Tree: {0:.2f}%".format(
        dtree.score(X_test, y_test) * 100
    )
    plt.title(acc_title, size=15)
    plt.tight_layout()
    path_cm = os.path.join(output_dir, "confusion_matrix_dtree.png")
    plt.savefig(path_cm, format="png", bbox_inches="tight")
    plt.close()
    print(f"Plot confusion matrix disimpan di: {path_cm}")

    return dtree


FOLDER_CATEGORY = {
    "building": "assets/Building",
    "cloud":    "assets/Cloud",
    "forest":   "assets/Forest",
    "mountain":  "assets/Mountain",
}


def run_mosaic(target_path, category, output_path, grid_m=64, grid_n=64,
               output_dir="output"):

    folder = FOLDER_CATEGORY.get(category.lower())
    if folder is None:
        raise ValueError(
            f"Kategori tidak diketahui: '{category}'. "
            f"Pilihan yang tersedia: {list(FOLDER_CATEGORY.keys())}"
        )

    os.makedirs("cache", exist_ok=True)
    cache_path = os.path.join("cache", f"{category}_avg.npz")
    
    if os.path.exists(cache_path):
        print(f"[1/4] Mengambil cache dari: {cache_path}")
        data      = np.load(cache_path, allow_pickle=True)
        avg_rgb   = data["avg_rgb"]
        img_paths = list(data["paths"])
    else:
        print(f"[1/4] Membaca dataset dari folder: {folder}")
        avg_rgb, img_paths = get_folder_avg_rgb(folder)
        np.savez(cache_path, avg_rgb=avg_rgb, paths=np.array(img_paths))
        print(f"Cache berhasil disimpan ke: {cache_path}")

    print("[2/4] Melatih model Decision Tree...")
    dtree = train_and_evaluate(avg_rgb, output_dir=output_dir)

    print(f"\n[3/4] Menghitung rata-rata RGB per grid dari: {target_path}")
    avg_color_pixel, width, height, grid_w, grid_h = get_avg_rgb_per_grid(
        target_path, grid_m, grid_n
    )

    print(f"[4/4] Memprediksi tile dan menyusun mosaik ke: {output_path}")
    flat    = avg_color_pixel.reshape(-1, 3)
    flat_df = pd.DataFrame(flat, columns=["R", "G", "B"])
    preds   = dtree.predict(flat_df)
    nearest = preds.reshape(grid_n, grid_m)

    result = mosaic(nearest, img_paths, width, height, grid_w, grid_h)
    result.save(output_path)
    print("Proses selesai.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Penggunaan: python main.py <target_image> <category> <output_path> [output_dir]")
        print("  category   : building | cloud | forest | mountain")
        print("  output_dir : folder untuk menyimpan plot (default: output)")
        sys.exit(1)

    out_dir = sys.argv[4] if len(sys.argv) >= 5 else "output"
    run_mosaic(sys.argv[1], sys.argv[2], sys.argv[3], output_dir=out_dir)