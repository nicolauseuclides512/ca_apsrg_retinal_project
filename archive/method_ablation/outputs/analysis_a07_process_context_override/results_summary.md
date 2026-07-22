# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.5907 ± 0.1225 0.0938 ± 0.0426 0.1577 ± 0.0630 0.0868 ± 0.0373 0.9325 ± 0.0093
CHASEDB1       CA-APSRG        28 0.5907 ± 0.1225 0.0938 ± 0.0426 0.1577 ± 0.0630 0.0868 ± 0.0373 0.9325 ± 0.0093
   DRIVE APSRG Baseline        20 0.7372 ± 0.1733 0.0835 ± 0.0512 0.1443 ± 0.0755 0.0795 ± 0.0465 0.8803 ± 0.0171
   DRIVE       CA-APSRG        20 0.7372 ± 0.1733 0.0835 ± 0.0512 0.1443 ± 0.0754 0.0795 ± 0.0464 0.8803 ± 0.0171
   STARE APSRG Baseline        20 0.6412 ± 0.2595 0.0903 ± 0.0847 0.1494 ± 0.1219 0.0856 ± 0.0786 0.9267 ± 0.0168
   STARE       CA-APSRG        20 0.6412 ± 0.2595 0.0903 ± 0.0847 0.1494 ± 0.1219 0.0856 ± 0.0786 0.9267 ± 0.0168
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28          0.000000e+00           0.000000             0.000000        0.000000                    0                28                     0
   DRIVE        20          6.649686e-07          -0.000014            -0.000015       -0.000012                    0                19                     1
   STARE        20          0.000000e+00           0.000000             0.000000        0.000000                    0                20                     0
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.590723       0.122484     0.093751    0.042579       0.157726      0.063041  0.086845 0.037312       0.932458      0.009343
CHASEDB1       CA-APSRG        28        0.590723       0.122484     0.093751    0.042579       0.157726      0.063041  0.086845 0.037312       0.932458      0.009343
   DRIVE APSRG Baseline        20        0.737245       0.173278     0.083526    0.051236       0.144276      0.075474  0.079537 0.046457       0.880279      0.017100
   DRIVE       CA-APSRG        20        0.737246       0.173278     0.083511    0.051186       0.144261      0.075425  0.079525 0.046418       0.880278      0.017100
   STARE APSRG Baseline        20        0.641153       0.259487     0.090306    0.084745       0.149395      0.121859  0.085624 0.078644       0.926664      0.016849
   STARE       CA-APSRG        20        0.641153       0.259487     0.090306    0.084745       0.149395      0.121859  0.085624 0.078644       0.926664      0.016849
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                                           comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01L_comparison.png           0.049692           0.049692             0.0              0.0           0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01R_comparison.png           0.076177           0.076177             0.0              0.0           0.0
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02L_comparison.png           0.135023           0.135023             0.0              0.0           0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02R_comparison.png           0.099368           0.099368             0.0              0.0           0.0
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03L_comparison.png           0.171196           0.171196             0.0              0.0           0.0
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03R_comparison.png           0.136606           0.136606             0.0              0.0           0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_04L_comparison.png           0.075405           0.075405             0.0              0.0           0.0
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_04R_comparison.png           0.226638           0.226638             0.0              0.0           0.0
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05L_comparison.png           0.154821           0.154821             0.0              0.0           0.0
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05R_comparison.png           0.073948           0.073948             0.0              0.0           0.0
```

## Worst F1 Drops

```text
 dataset  image_id                                                                                                                           comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   DRIVE        25           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\DRIVE\comparison\25_comparison.png           0.373320           0.373015       -0.000305         0.000013     -0.000284
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01L_comparison.png           0.049692           0.049692        0.000000         0.000000      0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02L_comparison.png           0.135023           0.135023        0.000000         0.000000      0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01R_comparison.png           0.076177           0.076177        0.000000         0.000000      0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03L_comparison.png           0.171196           0.171196        0.000000         0.000000      0.000000
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03R_comparison.png           0.136606           0.136606        0.000000         0.000000      0.000000
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_04L_comparison.png           0.075405           0.075405        0.000000         0.000000      0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02R_comparison.png           0.099368           0.099368        0.000000         0.000000      0.000000
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05L_comparison.png           0.154821           0.154821        0.000000         0.000000      0.000000
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05R_comparison.png           0.073948           0.073948        0.000000         0.000000      0.000000
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                           comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0002       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\STARE\comparison\im0002_comparison.png           0.004558           0.004558             0.0              0.0           0.0
   STARE    im0239       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\STARE\comparison\im0239_comparison.png           0.020149           0.020149             0.0              0.0           0.0
   STARE    im0235       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\STARE\comparison\im0235_comparison.png           0.033023           0.033023             0.0              0.0           0.0
   STARE    im0139       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\STARE\comparison\im0139_comparison.png           0.035495           0.035495             0.0              0.0           0.0
   DRIVE        32           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\DRIVE\comparison\32_comparison.png           0.040954           0.040954             0.0              0.0           0.0
   STARE    im0082       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\STARE\comparison\im0082_comparison.png           0.046732           0.046732             0.0              0.0           0.0
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01L_comparison.png           0.049692           0.049692             0.0              0.0           0.0
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\STARE\comparison\im0001_comparison.png           0.053103           0.053103             0.0              0.0           0.0
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_13R_comparison.png           0.057065           0.057065             0.0              0.0           0.0
   DRIVE        26           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\DRIVE\comparison\26_comparison.png           0.058256           0.058256             0.0              0.0           0.0
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                                           comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        25           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\DRIVE\comparison\25_comparison.png            0.703982            0.703996         0.000013     -0.000284       -0.000305
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01L_comparison.png            0.417434            0.417434         0.000000      0.000000        0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02L_comparison.png            0.470900            0.470900         0.000000      0.000000        0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01R_comparison.png            0.391814            0.391814         0.000000      0.000000        0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02R_comparison.png            0.521095            0.521095         0.000000      0.000000        0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03L_comparison.png            0.720813            0.720813         0.000000      0.000000        0.000000
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_04L_comparison.png            0.651929            0.651929         0.000000      0.000000        0.000000
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03R_comparison.png            0.575279            0.575279         0.000000      0.000000        0.000000
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05L_comparison.png            0.841763            0.841763         0.000000      0.000000        0.000000
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05R_comparison.png            0.691374            0.691374         0.000000      0.000000        0.000000
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                           comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01L_comparison.png            0.417434            0.417434              0.0           0.0             0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_01R_comparison.png            0.391814            0.391814              0.0           0.0             0.0
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02L_comparison.png            0.470900            0.470900              0.0           0.0             0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_02R_comparison.png            0.521095            0.521095              0.0           0.0             0.0
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03L_comparison.png            0.720813            0.720813              0.0           0.0             0.0
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_03R_comparison.png            0.575279            0.575279              0.0           0.0             0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_04L_comparison.png            0.651929            0.651929              0.0           0.0             0.0
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_04R_comparison.png            0.717775            0.717775              0.0           0.0             0.0
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05L_comparison.png            0.841763            0.841763              0.0           0.0             0.0
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a07_process_context_override\CHASEDB1\comparison\Image_05R_comparison.png            0.691374            0.691374              0.0           0.0             0.0
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a07_process_context_override\plots\delta_iou_by_dataset.png`
