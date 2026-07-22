# CA-APSRG Retinal Vessel Segmentation

**Context-Aware Automatic Polling Seeded Region Growing with Adaptive Morphological Refinement for Retinal Blood Vessel Segmentation**

Repository ini berisi implementasi penelitian untuk mengembangkan **Automatic Polling Seeded Region Growing (APSRG)** menjadi **Context-Aware APSRG (CA-APSRG)** pada segmentasi pembuluh darah retina.

Metode yang dikembangkan menggabungkan:

- preprocessing citra fundus berbasis kanal hijau, normalisasi, CLAHE, dan denoising;
- multi-scale black-hat vessel enhancement;
- fuzzy SRG feature support;
- Harris Corner automatic seed polling;
- selective fuzzy–Harris seed selection;
- edge-delayed priority region growing;
- local-or-region acceptance;
- context feature extraction;
- adaptive morphological refinement;
- evaluasi lintas dataset DRIVE, STARE, dan CHASEDB1;
- method ablation dan recovery ablation;
- visualisasi hasil melalui Streamlit.

> **Research status:** konfigurasi **R04** saat ini menjadi kandidat utama yang paling stabil secara rata-rata lintas dataset.

---

## 1. Tujuan Penelitian

Penelitian ini bertujuan mengembangkan APSRG menjadi CA-APSRG melalui penyempurnaan:

1. pemilihan seed otomatis berbasis fuzzy SRG dan Harris Corner;
2. pengendalian jumlah serta distribusi seed;
3. region growing berbasis priority queue dan connected-edge information;
4. local-or-region intensity acceptance untuk mempertahankan kontinuitas pembuluh;
5. adaptive morphological refinement berbasis konteks hasil segmentasi;
6. evaluasi kontribusi setiap komponen melalui eksperimen ablasi.

Rumusan tujuan yang digunakan:

> Mengembangkan metode Context-Aware Automatic Polling Seeded Region Growing untuk segmentasi pembuluh darah retina melalui selective fuzzy–Harris seed polling, edge-delayed region growing, dan adaptive morphological refinement berbasis konteks, serta mengevaluasi kontribusi setiap komponennya pada dataset DRIVE, STARE, dan CHASEDB1.

---

## 2. Kontribusi Utama

Kontribusi implementasi dalam repository ini meliputi:

1. **Fuzzy SRG support**
   - connected-edge map;
   - not-connected-edge map;
   - fuzzy similarity map;
   - fuzzy threshold;
   - fuzzy seed support.

2. **Selective fuzzy–Harris seed polling**
   - Harris Corner digunakan untuk polling seed yang didukung fuzzy region;
   - kandidat diranking berdasarkan fuzzy score, Harris response, dan vesselness;
   - seed dipilih secara spasial dengan minimum distance;
   - controlled fallback digunakan untuk memenuhi jumlah target seed.

3. **Edge-delayed region growing**
   - kandidat diproses dengan priority queue;
   - prioritas dapat menggunakan `kang_product`, `additive`, atau `hybrid`;
   - pertumbuhan tetap dibatasi candidate vessel map dan FoV;
   - connected-edge membership menunda pemrosesan piksel edge.

4. **Local-or-region acceptance**
   - kandidat diterima bila konsisten terhadap lintasan lokal atau mean region yang lebih toleran;
   - mekanisme ini mengurangi under-segmentation yang muncul pada region-mean-only acceptance.

5. **Context-aware refinement**
   - vessel density;
   - connected-component statistics;
   - small-component ratio;
   - APSRG process context;
   - adaptive morphological parameter selection.

6. **Controlled ablation**
   - adaptive morphology experiments;
   - method ablation A01–A07;
   - recovery ablation R00–R06;
   - paired comparison;
   - win–tie–loss;
   - Wilcoxon signed-rank test;
   - 95% bootstrap confidence interval.

---

## 3. Alur Metode

```text
Input Fundus Image
        ↓
Green Channel Extraction
        ↓
Intensity Normalization
        ↓
CLAHE
        ↓
Denoising
        ↓
FoV Masking
        ↓
Multi-scale Black-hat Vessel Enhancement
        ↓
Candidate Vessel Map
        ↓
Fuzzy SRG Feature Support
        ↓
Harris Corner Candidate Polling
        ↓
Selective Fuzzy–Harris Seed Selection
        ↓
Seed Dilation
        ↓
Edge-delayed Priority Region Growing
        ↓
Local-or-Region Acceptance
        ↓
APSRG Mask
        ↓
Context Feature Extraction
        ↓
Adaptive Morphological Refinement
        ↓
CA-APSRG Mask
        ↓
Evaluation and Statistical Analysis
```

---

## 4. Kandidat Konfigurasi Utama

Konfigurasi stabil saat ini adalah **R04**:

```text
Selective fuzzy–Harris seed polling
→ target 77 seed points
→ seed dilation radius 1
→ edge-delayed region growing
→ Kang-product priority
→ local-or-region acceptance
→ conservative adaptive morphology
```

File konfigurasi yang disarankan:

```text
configs/final_candidate_r04.yaml
```

Apabila file tersebut belum tersedia atau belum terisi, gunakan:

```text
configs/recovery_ablation/r04_local_or_region.yaml
```

Parameter inti:

```yaml
apsrg_baseline:
  seed_selection_method: selective_fuzzy_harris
  region_growing_mode: edge_delayed
  max_intensity_difference: 18

  hybrid_seed:
    enabled: true
    target_seed_count: 77
    min_seed_count: 7
    max_seed_count: 77
    fuzzy_support_radius: 2
    relaxed_support_radius: 5
    min_seed_distance: 3
    fuzzy_weight: 0.35
    harris_weight: 0.40
    vesselness_weight: 0.25
    allow_relaxed_harris_fallback: true
    allow_fuzzy_fallback: true
    seed_dilate_radius: 1

  edge_delayed_region_growing:
    enabled: true
    priority_mode: kang_product
    fuzzy_distance_scale: 0.4
    connected_edge_wd: 0.4
    edge_floor: 0.05
    edge_weight: 0.35
    acceptance_mode: local_or_region
    region_mean_tolerance_multiplier: 2.0
    max_fuzzy_distance: 1.0
    recompute_priority: true
    priority_tolerance: 0.000001
    record_growth_order: true
```

Untuk menjaga hasil refinement tetap konservatif:

```yaml
ca_apsrg:
  enabled: true
  always_refine: true

  process_context:
    enabled: true
    can_trigger_refinement: true
    can_override_refinement_level: false
```

---

## 5. Dataset

Evaluasi dilakukan pada tiga dataset segmentasi pembuluh retina:

| Dataset | Jumlah citra evaluasi | Karakteristik umum |
|---|---:|---|
| DRIVE | 20 | Citra fundus dengan anotasi manual dan FoV mask |
| STARE | 20 | Variasi patologis dan struktur pembuluh yang kompleks |
| CHASEDB1 | 28 | Citra retina anak dengan dua citra per subjek |
| **Total** | **68** | Digunakan dalam evaluasi lintas dataset |

Dataset tidak disertakan langsung dalam repository. Pengguna harus memperoleh dataset dari sumber resminya dan mematuhi ketentuan penggunaannya.

Struktur awal yang disarankan:

```text
data/
├── raw/
│   └── Retinal Vessel/
│       ├── DRIVE/
│       ├── STARE/
│       └── CHASEDB1/
├── working_png/
└── manifests/
    └── manifest.csv
```

---

## 6. Ringkasan Hasil Utama

### 6.1 R00 versus R04 — CA-APSRG

| Dataset | R00 F1 | R04 F1 | R00 IoU | R04 IoU |
|---|---:|---:|---:|---:|
| CHASEDB1 | 0.5578 | **0.6016** | 0.3875 | **0.4318** |
| DRIVE | 0.6972 | **0.7056** | 0.5383 | **0.5473** |
| STARE | **0.6454** | 0.6435 | **0.4853** | 0.4765 |

R04 memberikan peningkatan rata-rata lintas dataset, dengan peningkatan paling jelas pada CHASEDB1 dan peningkatan kecil pada DRIVE. Pada STARE, performa relatif setara tetapi sedikit lebih rendah daripada R00.

### 6.2 Metrik R04 — CA-APSRG

| Dataset | Accuracy | Precision | Recall | F1-score | IoU |
|---|---:|---:|---:|---:|---:|
| CHASEDB1 | 0.9449 | 0.6036 | 0.6089 | 0.6016 | 0.4318 |
| DRIVE | 0.9238 | 0.6804 | 0.7398 | 0.7056 | 0.5473 |
| STARE | 0.9307 | 0.5262 | 0.8393 | 0.6435 | 0.4765 |

### 6.3 Temuan Ablasi

- **R01 → R02:** peningkatan jumlah seed menjadi 77 dan radius 1 berhasil meningkatkan cakupan pembuluh.
- **R02 → R03:** region-mean-only acceptance menghasilkan under-segmentation yang kuat.
- **R03 → R04:** local-or-region acceptance memulihkan recall, F1, dan IoU.
- **R04 → R05:** hybrid priority tidak memberikan keuntungan konsisten dibanding Kang-product priority.
- **R04 → R06:** process-context override menghasilkan mask yang identik pada eksperimen saat ini.
- Adaptive morphology bersifat konservatif dan hanya mengubah sejumlah kecil piksel.

Klaim hasil yang disarankan:

> Selective fuzzy–Harris seed polling combined with local-or-region edge-delayed region growing improved the average cross-dataset segmentation balance, with the clearest gains observed on CHASEDB1.

---

## 7. Struktur Repository

```text
ca_apsrg_retinal_project/
├── app.py
├── README.md
├── requirements.txt
├── PROJECT_TREE.txt
├── configs/
│   ├── default.yaml
│   ├── final_candidate_r04.yaml
│   ├── experiments/
│   ├── method_ablation/
│   └── recovery_ablation/
├── data/
│   ├── raw/
│   ├── working_png/
│   └── manifests/
├── notebooks/
├── outputs/
│   ├── analysis/
│   ├── experiments/
│   ├── method_ablation/
│   ├── recovery_ablation/
│   ├── reports/
│   └── single_test/
├── scripts/
│   ├── 00_convert_all_to_png.py
│   ├── 01_build_manifest.py
│   ├── 02_run_single_image.py
│   ├── 03_run_batch.py
│   ├── 04_summarize_results.py
│   ├── 05_run_all_experiments.py
│   ├── 06_run_method_ablation.py
│   ├── 07_run_recovery_ablation.py
│   └── 08_export_process_context_diagnostics.py
├── src/
│   ├── data/
│   ├── evaluation/
│   ├── pipeline/
│   ├── preprocessing/
│   ├── segmentation/
│   │   ├── adaptive_morphology.py
│   │   ├── apsrg_baseline.py
│   │   ├── apsrg_harris.py
│   │   ├── apsrg_process_context.py
│   │   ├── ca_apsrg.py
│   │   ├── context_features.py
│   │   ├── edge_delayed_region_growing.py
│   │   ├── hybrid_seed_selection.py
│   │   ├── srg_features.py
│   │   └── skimage_compat.py
│   ├── ui/
│   │   ├── streamlit_helpers.py
│   │   └── recovery_ablation_viewer.py
│   └── utils/
└── tests/
```

Beberapa file yang disebutkan di atas merupakan file pada versi metode terbaru. Pastikan semuanya sudah dikomit sebelum deployment atau reproduksi penuh.

---

## 8. Persyaratan Sistem

Disarankan:

- Python 3.10 atau 3.11;
- Windows, Linux, atau macOS;
- RAM minimal 8 GB;
- penyimpanan yang cukup untuk dataset dan output eksperimen;
- CPU multi-core;
- GPU tidak wajib.

Dependency utama:

```text
numpy
pandas
scipy
opencv-python-headless
Pillow
scikit-image
imageio
tifffile
matplotlib
PyYAML
tqdm
streamlit
pytest
```

---

## 9. Instalasi

### 9.1 Clone repository

```bash
git clone https://github.com/nicolauseuclides512/ca_apsrg_retinal_project.git
cd ca_apsrg_retinal_project
```

### 9.2 Buat virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 9.3 Install dependency

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 9.4 Periksa instalasi

```bash
python -c "import cv2, numpy, pandas, scipy, skimage, streamlit; print('Environment OK')"
```

---

## 10. Persiapan Data

### 10.1 Letakkan dataset asli

```text
data/raw/Retinal Vessel/
```

Jangan mengubah atau menimpa dataset asli.

### 10.2 Konversi seluruh citra ke PNG

```bash
python scripts/00_convert_all_to_png.py \
  --input-root "data/raw/Retinal Vessel" \
  --output-root "data/working_png" \
  --copy-png \
  --binarize-masks
```

PowerShell satu baris:

```powershell
python scripts/00_convert_all_to_png.py --input-root "data/raw/Retinal Vessel" --output-root "data/working_png" --copy-png --binarize-masks
```

Script akan:

- membaca folder secara rekursif;
- mengonversi PPM, JPG, JPEG, TIFF, GIF, dan BMP ke PNG;
- melewati arsip;
- mempertahankan struktur relatif;
- membinarisasi mask;
- membuat laporan konversi.

Laporan:

```text
outputs/reports/png_conversion_report.csv
```

### 10.3 Buat manifest

```bash
python scripts/01_build_manifest.py \
  --working-root "data/working_png" \
  --output "data/manifests/manifest.csv"
```

PowerShell satu baris:

```powershell
python scripts/01_build_manifest.py --working-root "data/working_png" --output "data/manifests/manifest.csv"
```

Kolom utama manifest:

```text
dataset
image_id
image_path
mask_path
fov_path
```

---

## 11. Menjalankan Satu Citra

Menggunakan manifest:

```powershell
python scripts/02_run_single_image.py `
  --manifest "data/manifests/manifest.csv" `
  --dataset DRIVE `
  --image-id 23 `
  --config "configs/recovery_ablation/r04_local_or_region.yaml"
```

Versi satu baris:

```powershell
python scripts/02_run_single_image.py --manifest "data/manifests/manifest.csv" --dataset DRIVE --image-id 23 --config "configs/recovery_ablation/r04_local_or_region.yaml"
```

Dengan final candidate:

```powershell
python scripts/02_run_single_image.py --manifest "data/manifests/manifest.csv" --dataset DRIVE --image-id 23 --config "configs/final_candidate_r04.yaml"
```

Output umumnya disimpan pada:

```text
outputs/single_test/
├── DRIVE/
│   ├── baseline_masks/
│   ├── ca_apsrg_masks/
│   ├── comparison/
│   ├── debug/
│   ├── overlays/
│   └── preprocessed/
└── metrics_per_image.csv
```

---

## 12. Menjalankan Batch

### 12.1 Satu dataset

```powershell
python scripts/03_run_batch.py `
  --manifest "data/manifests/manifest.csv" `
  --dataset DRIVE `
  --config "configs/final_candidate_r04.yaml" `
  --output-dir "outputs/final_candidate_r04"
```

### 12.2 Tiga dataset

```powershell
python scripts/03_run_batch.py `
  --manifest "data/manifests/manifest.csv" `
  --dataset DRIVE `
  --dataset STARE `
  --dataset CHASEDB1 `
  --config "configs/final_candidate_r04.yaml" `
  --output-dir "outputs/final_candidate_r04"
```

Apabila script PowerShell tersedia:

```powershell
.\run_final_candidate_all_datasets.ps1
```

---

## 13. Merangkum Hasil

```powershell
python scripts/04_summarize_results.py `
  --results "outputs/final_candidate_r04/metrics_per_image.csv" `
  --output-dir "outputs/final_candidate_r04/analysis"
```

Output analisis dapat mencakup:

```text
metrics_summary.csv
summary_by_dataset_method.csv
improvement_by_dataset.csv
improvement_per_image.csv
long_metrics.csv
plots/
```

---

## 14. Eksperimen Adaptive Morphology

Eksperimen adaptive morphology lama tetap dipertahankan untuk reproduksi:

```powershell
python scripts/05_run_all_experiments.py
```

Eksperimen tersebut mengevaluasi konfigurasi:

```text
Experiment 1  Recall-oriented
Experiment 2  Precision-oriented
Experiment 3  Balanced main result
Experiment 4  Static morphology
Experiment 5  No skeleton guard
Experiment 6  No small-component removal
```

---

## 15. Method Ablation A01–A07

```powershell
python scripts/06_run_method_ablation.py `
  --dataset DRIVE `
  --dataset STARE `
  --dataset CHASEDB1 `
  --clean
```

Rancangan method ablation:

| Kode | Seed selection | Region growing | Tujuan |
|---|---|---|---|
| A01 | Percentile-polling | BFS | APSRG lama |
| A02 | Harris polling | BFS | Kontribusi Harris |
| A03 | Fuzzy SRG | BFS | Kontribusi fuzzy support |
| A04 | Selective fuzzy–Harris | BFS | Kontribusi selective hybrid |
| A05 | Selective fuzzy–Harris | Edge-delayed | Kontribusi edge-delayed |
| A06 | A05 + process context logging | Edge-delayed | Sanity check |
| A07 | A05 + process override | Edge-delayed | Context override |

Output:

```text
outputs/method_ablation/
├── experiments_a01_legacy_polling_bfs/
├── ...
├── experiments_a07_process_context_override/
└── comparison/
    ├── ablation_article_table.csv
    ├── ablation_delta_vs_reference.csv
    ├── ablation_per_image_long.csv
    └── ablation_summary_long.csv
```

---

## 16. Recovery Ablation R00–R06

Jalankan seluruh recovery ablation:

```powershell
python scripts/07_run_recovery_ablation.py `
  --dataset DRIVE `
  --dataset STARE `
  --dataset CHASEDB1 `
  --clean
```

Versi satu baris:

```powershell
python scripts/07_run_recovery_ablation.py --dataset DRIVE --dataset STARE --dataset CHASEDB1 --clean
```

Rancangan recovery ablation:

| Kode | Konfigurasi | Tujuan |
|---|---|---|
| R00 | Legacy percentile-polling + BFS | Kontrol utama |
| R01 | Selective fuzzy–Harris, 35 seed, radius 0 + BFS | Seed terbatas |
| R02 | Selective fuzzy–Harris, 77 seed, radius 1 + BFS | Pemulihan cakupan seed |
| R03 | R02 + edge-delayed region-mean | Kontrol acceptance lama |
| R04 | R02 + edge-delayed local-or-region | Kandidat utama |
| R05 | R04 + hybrid priority | Uji mode prioritas |
| R06 | R04 + process-context override | Uji context override |

Bangun ulang tabel tanpa mengulang segmentasi:

```powershell
python scripts/07_run_recovery_ablation.py --skip-run
```

Output utama:

```text
outputs/recovery_ablation/comparison/
├── recovery_per_image_long.csv
├── recovery_summary_long.csv
├── recovery_article_table.csv
├── recovery_delta_vs_r00.csv
└── recovery_stage_deltas.csv
```

Tabel perbandingan berpasangan memuat:

- mean delta;
- median delta;
- standard deviation;
- wins;
- ties;
- losses;
- Wilcoxon signed-rank test;
- 95% bootstrap confidence interval.

---

## 17. Process-Context Diagnostics

```powershell
python scripts/08_export_process_context_diagnostics.py
```

Output:

```text
outputs/recovery_ablation/process_context_diagnostics/
├── process_context_per_image.csv
├── process_context_summary.csv
└── process_context_level_counts.csv
```

Analisis ini digunakan untuk memeriksa:

- candidate density;
- growth ratio;
- connected-edge density;
- process-risk score;
- process-risk level;
- mask refinement level;
- process refinement level;
- combined refinement level;
- jumlah piksel yang ditambah atau dihapus.

Temuan saat ini menunjukkan bahwa threshold process context masih terlalu tinggi untuk distribusi data aktual, sehingga sebagian besar citra memperoleh risk level rendah dan refinement level normal.

---

## 18. Streamlit Application

Jalankan:

```bash
streamlit run app.py
```

Menu dasar:

```text
Home
Single Image Demo
Batch Result Viewer
Method Explanation
About Dataset
```

Pada versi UI terbaru, menu berikut juga tersedia:

```text
Recovery Ablation R00-R06
```

Agar recovery viewer aktif, pastikan:

```text
src/ui/recovery_ablation_viewer.py
```

tersedia dan `app.py` sudah mengimpornya.

Fitur Streamlit terbaru:

- upload citra fundus;
- upload ground truth dan FoV mask;
- menjalankan APSRG dan CA-APSRG;
- menampilkan preprocessed image;
- vesselness map;
- seed map;
- candidate map;
- APSRG mask;
- CA-APSRG mask;
- overlays;
- perbandingan metrik;
- debug/context features;
- viewer hasil batch;
- ranking R00–R06;
- APSRG versus CA-APSRG;
- stage analysis;
- delta versus R00;
- image browser;
- process-context diagnostics;
- CSV tables.

Untuk konsistensi pipeline, pemanggilan CA-APSRG pada Streamlit harus meneruskan debug APSRG:

```python
refined_mask, ca_debug = ca_apsrg_refine(
    baseline_mask,
    fov_mask=fov_for_segmentation,
    params=adaptive_cfg,
    ca_config=ca_cfg,
    context_config=context_cfg,
    apsrg_debug=apsrg_debug,
)
```

---

## 19. Evaluasi

Metrik yang digunakan:

```text
Accuracy
Precision
Recall / Sensitivity
Specificity
F1-score
Intersection over Union
```

Fokus interpretasi utama:

1. F1-score;
2. IoU;
3. precision;
4. recall;
5. accuracy.

Accuracy tidak digunakan sebagai indikator utama karena jumlah piksel background jauh lebih besar daripada piksel pembuluh.

---

## 20. Reproducibility

Setiap eksperimen sebaiknya menyimpan:

```text
resolved_pipeline_config.yaml
metrics_per_image.csv
metrics_summary.csv
batch_manifest_used.csv
baseline_masks/
ca_apsrg_masks/
overlays/
comparison/
debug/
```

Validasi konfigurasi:

```powershell
python -c "from src.pipeline.run_pipeline import load_pipeline_config; c=load_pipeline_config('configs/recovery_ablation/r04_local_or_region.yaml'); print(c.apsrg.seed_selection_method); print(c.apsrg.region_growing_mode); print(c.apsrg.hybrid_seed.target_seed_count); print(c.apsrg.edge_delayed_region_growing.acceptance_mode)"
```

Hasil yang diharapkan:

```text
selective_fuzzy_harris
edge_delayed
77
local_or_region
```

---

## 21. Pemeriksaan Kode

```powershell
python -m py_compile src/segmentation/apsrg_harris.py
python -m py_compile src/segmentation/srg_features.py
python -m py_compile src/segmentation/hybrid_seed_selection.py
python -m py_compile src/segmentation/edge_delayed_region_growing.py
python -m py_compile src/segmentation/apsrg_process_context.py
python -m py_compile src/segmentation/apsrg_baseline.py
python -m py_compile src/segmentation/adaptive_morphology.py
python -m py_compile src/segmentation/ca_apsrg.py
python -m py_compile src/pipeline/run_pipeline.py
python -m py_compile scripts/07_run_recovery_ablation.py
python -m py_compile scripts/08_export_process_context_diagnostics.py
python -m py_compile app.py
```

Jalankan test:

```bash
pytest -q
```

---

## 22. Prinsip Format Gambar

Gunakan PNG sebagai format kerja utama:

- citra fundus: PNG RGB 8-bit;
- ground truth mask: PNG biner 0/255;
- FoV mask: PNG biner 0/255;
- hasil segmentasi: PNG biner 0/255;
- overlay dan comparison: PNG.

Jangan menggunakan JPG untuk ground truth atau hasil segmentasi karena kompresi lossy dapat mengubah piksel mask.

---

## 23. Git dan Output Eksperimen

Contoh `.gitignore`:

```gitignore
.venv/
venv/
__pycache__/
*.pyc
.idea/

data/raw/
data/working_png/

outputs/*

!outputs/analysis/
!outputs/analysis/**

!outputs/analysis_exp*/
!outputs/analysis_exp*/**

!outputs/experiments/
!outputs/experiments/**

!outputs/experiments_exp*/
!outputs/experiments_exp*/**

!outputs/method_ablation/
!outputs/method_ablation/**

!outputs/recovery_ablation/
!outputs/recovery_ablation/**

!outputs/final_candidate_r04/
!outputs/final_candidate_r04/**

*.log
```

Periksa file yang masih diabaikan:

```bash
git check-ignore -v outputs/recovery_ablation/comparison/recovery_article_table.csv
```

---

## 24. Keterbatasan

1. Peningkatan tidak sama kuat pada seluruh dataset.
2. R04 meningkatkan hasil rata-rata, tetapi sedikit menurun pada STARE dibanding R00.
3. Adaptive morphology hanya menghasilkan perubahan kecil terhadap mask akhir.
4. Process-context override belum memberikan perubahan hasil pada eksperimen saat ini.
5. Threshold process context belum dikalibrasi terhadap distribusi aktual.
6. Evaluasi masih bergantung pada tiga dataset publik.
7. Metode belum ditujukan sebagai alat diagnosis klinis.

---

## 25. Future Work

1. Kalibrasi threshold process context berdasarkan distribusi per dataset.
2. Confidence-aware refinement untuk false positive yang tetap terhubung.
3. Vessel-width-aware region growing.
4. Skeleton topology and branch continuity analysis.
5. Cross-dataset parameter transfer.
6. Evaluasi robust terhadap noise, illumination, dan pathology.
7. Tambahan dataset seperti HRF atau IOSTAR.
8. Perbandingan dengan metode deep learning.
9. Optimasi waktu komputasi priority-queue growing.
10. Packaging dan deployment Streamlit yang lebih stabil.

---

## 26. Penggunaan untuk Penelitian

Repository ini ditujukan untuk:

- eksperimen akademik;
- penelitian segmentasi pembuluh retina;
- studi perbandingan APSRG dan CA-APSRG;
- analisis kontribusi komponen;
- reproduksi hasil;
- penyusunan artikel ilmiah.

Repository ini **bukan alat diagnosis medis** dan hasil segmentasi tidak boleh digunakan sebagai satu-satunya dasar keputusan klinis.

---

## 27. Citation

Apabila repository ini digunakan dalam penelitian, cantumkan sitasi repository dan artikel yang dihasilkan.

Template BibTeX sementara:

```bibtex
@software{ca_apsrg_retinal_project,
  author  = {Nicolaus Euclides Wahyu Nugroho},
  title   = {CA-APSRG Retinal Vessel Segmentation Project},
  year    = {2026},
  url     = {https://github.com/nicolauseuclides512/ca_apsrg_retinal_project},
  note    = {Context-Aware Automatic Polling Seeded Region Growing with Adaptive Morphological Refinement}
}
```

Sitasi artikel dapat ditambahkan setelah naskah diterbitkan.

---

## 28. Maintainer

**Nicolaus Euclides Wahyu Nugroho**

Repository:

```text
https://github.com/nicolauseuclides512/ca_apsrg_retinal_project
```

---

## 29. License

Repository belum mencantumkan file lisensi secara eksplisit. Tambahkan `LICENSE` sebelum distribusi ulang yang lebih luas. Untuk penelitian akademik, hubungi maintainer terkait ketentuan penggunaan kode dan hasil eksperimen.