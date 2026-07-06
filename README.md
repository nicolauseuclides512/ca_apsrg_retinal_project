# CA-APSRG Retinal Vessel Segmentation Project

Project Python ini dirancang untuk penelitian:

**Context-Aware Automatic Polling Seeded Region Growing (CA-APSRG) dengan Adaptive Morphological Refinement untuk Segmentasi Pembuluh Darah Retina.**

Alur utama mengikuti proposal:

1. Input citra fundus retina
2. Pre-processing
3. Implementasi APSRG baseline
4. Analisis false positive
5. CA-APSRG
6. Adaptive Morphological Refinement
7. Evaluasi kinerja

> Catatan: Implementasi APSRG di project ini masih berupa baseline awal yang dapat dijalankan. Detail APSRG asli dari paper/proposal dapat diisi dan disempurnakan bertahap pada file `src/segmentation/apsrg_baseline.py`.

---

## 1. Persiapan PyCharm

1. Buat folder project atau ekstrak ZIP ini.
2. Buka folder ini melalui PyCharm.
3. Buat virtual environment:
   - `File > Settings > Project > Python Interpreter > Add Interpreter`
4. Install dependency:

```bash
pip install -r requirements.txt
```

---

## 2. Struktur folder data yang disarankan

Jangan ubah dataset asli. Letakkan dataset asli di:

```text
data/raw/Retinal Vessel/
```

Hasil konversi PNG akan masuk ke:

```text
data/working_png/
```

Manifest eksperimen akan masuk ke:

```text
data/manifests/manifest.csv
```

Hasil segmentasi dan evaluasi akan masuk ke:

```text
outputs/
```

---

## 3. Konversi semua citra ke PNG

Gunakan script berikut:

```bash
python scripts/00_convert_all_to_png.py --input-root "data/raw/Retinal Vessel" --output-root "data/working_png" --copy-png --binarize-masks
```

Script ini akan:

- membaca folder secara rekursif,
- mengonversi `.ppm`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.gif`, `.bmp` ke `.png`,
- melewati arsip seperti `.gz`, `.7z`, `.zip`, `.tar`,
- tidak menimpa file PNG yang sudah ada,
- membuat laporan konversi di `outputs/reports/png_conversion_report.csv`.

---

## 4. Membuat manifest eksperimen

```bash
python scripts/01_build_manifest.py --working-root "data/working_png" --output "data/manifests/manifest.csv"
```

Manifest berisi pasangan:

- `image_path`
- `mask_path`
- `fov_path`
- `dataset`
- `image_id`

Untuk dataset DRIVE, STARE, dan CHASEDB1, script sudah menyiapkan aturan pairing awal. Bila nama folder berbeda, silakan sesuaikan di `src/data/manifest_builder.py`.

---

## 5. Menjalankan eksperimen satu gambar

```bash
python scripts/02_run_single_image.py ^
  --image "data/working_png/DRIVE/DRIVE/training/images/21_training.png" ^
  --mask "data/working_png/DRIVE/DRIVE/training/1st_manual/21_manual1.png" ^
  --fov "data/working_png/DRIVE/DRIVE/training/mask/21_training_mask.png" ^
  --output-dir "outputs/single_test"
```

Untuk Linux/Mac, ganti `^` dengan `\`.

---

## 6. Menjalankan eksperimen batch

```bash
python scripts/03_run_batch.py --manifest "data/manifests/manifest.csv" --output-dir "outputs/experiments"
```

Hasil utama:

```text
outputs/experiments/metrics_summary.csv
outputs/experiments/baseline_masks/
outputs/experiments/ca_apsrg_masks/
outputs/experiments/overlays/
```

---

## 7. File yang perlu diisi/ditingkatkan bertahap

Prioritas pengembangan:

1. `src/segmentation/apsrg_baseline.py`  
   Isi detail APSRG asli: polling seed otomatis, thresholding, region growing.

2. `src/segmentation/ca_apsrg.py`  
   Isi aturan context-aware: vessel density, connected component statistics, adaptive parameter selection.

3. `src/segmentation/adaptive_morphology.py`  
   Perbaiki aturan adaptive morphological refinement.

4. `src/evaluation/metrics.py`  
   Tambahkan AUC, MCC, specificity, dan uji statistik bila diperlukan.

---

## 8. Prinsip format gambar

Untuk penelitian ini, gunakan PNG sebagai format kerja utama:

- citra fundus: PNG RGB 8-bit,
- ground truth mask: PNG biner 0/255,
- FoV mask: PNG biner 0/255,
- hasil segmentasi: PNG biner 0/255.

Jangan simpan mask atau hasil segmentasi sebagai JPG.
