# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\experiments\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.4501 ± 0.0498 0.7066 ± 0.0507 0.5469 ± 0.0335 0.3771 ± 0.0322 0.9197 ± 0.0060
CHASEDB1       CA-APSRG        28 0.4501 ± 0.0498 0.7066 ± 0.0507 0.5469 ± 0.0335 0.3771 ± 0.0322 0.9197 ± 0.0060
   DRIVE APSRG Baseline        20 0.7112 ± 0.1099 0.6943 ± 0.0491 0.6970 ± 0.0632 0.5381 ± 0.0687 0.9246 ± 0.0169
   DRIVE       CA-APSRG        20 0.7112 ± 0.1099 0.6943 ± 0.0491 0.6970 ± 0.0632 0.5381 ± 0.0687 0.9246 ± 0.0169
   STARE APSRG Baseline        20 0.5356 ± 0.1401 0.8348 ± 0.0485 0.6413 ± 0.1157 0.4816 ± 0.1197 0.9286 ± 0.0245
   STARE       CA-APSRG        20 0.5356 ± 0.1401 0.8348 ± 0.0485 0.6413 ± 0.1157 0.4816 ± 0.1197 0.9286 ± 0.0245
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28                   0.0                0.0                  0.0             0.0                    0                28                     0
   DRIVE        20                   0.0                0.0                  0.0             0.0                    0                20                     0
   STARE        20                   0.0                0.0                  0.0             0.0                    0                20                     0
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.450081       0.049781     0.706640    0.050733       0.546873      0.033486  0.377057 0.032215       0.919714      0.005993
CHASEDB1       CA-APSRG        28        0.450081       0.049781     0.706640    0.050733       0.546873      0.033486  0.377057 0.032215       0.919714      0.005993
   DRIVE APSRG Baseline        20        0.711187       0.109914     0.694250    0.049080       0.696985      0.063221  0.538063 0.068692       0.924645      0.016884
   DRIVE       CA-APSRG        20        0.711187       0.109914     0.694250    0.049080       0.696985      0.063221  0.538063 0.068692       0.924645      0.016884
   STARE APSRG Baseline        20        0.535552       0.140052     0.834849    0.048525       0.641263      0.115718  0.481612 0.119730       0.928647      0.024468
   STARE       CA-APSRG        20        0.535552       0.140052     0.834849    0.048525       0.641263      0.115718  0.481612 0.119730       0.928647      0.024468
```

## Best F1 Improvements

```text
 dataset  image_id                                                                              comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01L_comparison.png           0.552080           0.552080             0.0              0.0           0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png           0.542630           0.542630             0.0              0.0           0.0
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02L_comparison.png           0.527916           0.527916             0.0              0.0           0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png           0.514027           0.514027             0.0              0.0           0.0
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03L_comparison.png           0.630453           0.630453             0.0              0.0           0.0
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03R_comparison.png           0.585963           0.585963             0.0              0.0           0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04L_comparison.png           0.558253           0.558253             0.0              0.0           0.0
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png           0.529906           0.529906             0.0              0.0           0.0
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05L_comparison.png           0.582166           0.582166             0.0              0.0           0.0
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05R_comparison.png           0.617387           0.617387             0.0              0.0           0.0
```

## Worst F1 Drops

```text
 dataset  image_id                                                                              comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01L_comparison.png           0.552080           0.552080             0.0              0.0           0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png           0.542630           0.542630             0.0              0.0           0.0
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02L_comparison.png           0.527916           0.527916             0.0              0.0           0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png           0.514027           0.514027             0.0              0.0           0.0
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03L_comparison.png           0.630453           0.630453             0.0              0.0           0.0
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03R_comparison.png           0.585963           0.585963             0.0              0.0           0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04L_comparison.png           0.558253           0.558253             0.0              0.0           0.0
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png           0.529906           0.529906             0.0              0.0           0.0
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05L_comparison.png           0.582166           0.582166             0.0              0.0           0.0
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05R_comparison.png           0.617387           0.617387             0.0              0.0           0.0
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                              comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0319_comparison.png           0.387167           0.387167             0.0              0.0           0.0
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0291_comparison.png           0.422421           0.422421             0.0              0.0           0.0
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14R_comparison.png           0.484300           0.484300             0.0              0.0           0.0
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\23_comparison.png           0.496393           0.496393             0.0              0.0           0.0
CHASEDB1 Image_11L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_11L_comparison.png           0.505614           0.505614             0.0              0.0           0.0
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_10L_comparison.png           0.508716           0.508716             0.0              0.0           0.0
CHASEDB1 Image_11R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_11R_comparison.png           0.512176           0.512176             0.0              0.0           0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png           0.514027           0.514027             0.0              0.0           0.0
CHASEDB1 Image_10R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_10R_comparison.png           0.518160           0.518160             0.0              0.0           0.0
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_09L_comparison.png           0.519409           0.519409             0.0              0.0           0.0
```

## Best Precision Improvements

```text
 dataset  image_id                                                                              comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01L_comparison.png            0.442494            0.442494              0.0           0.0             0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png            0.457908            0.457908              0.0           0.0             0.0
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02L_comparison.png            0.455870            0.455870              0.0           0.0             0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png            0.446289            0.446289              0.0           0.0             0.0
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03L_comparison.png            0.554676            0.554676              0.0           0.0             0.0
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03R_comparison.png            0.508809            0.508809              0.0           0.0             0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04L_comparison.png            0.467894            0.467894              0.0           0.0             0.0
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png            0.448740            0.448740              0.0           0.0             0.0
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05L_comparison.png            0.513906            0.513906              0.0           0.0             0.0
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05R_comparison.png            0.562237            0.562237              0.0           0.0             0.0
```

## Worst Precision Drops

```text
 dataset  image_id                                                                              comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01L_comparison.png            0.442494            0.442494              0.0           0.0             0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png            0.457908            0.457908              0.0           0.0             0.0
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02L_comparison.png            0.455870            0.455870              0.0           0.0             0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png            0.446289            0.446289              0.0           0.0             0.0
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03L_comparison.png            0.554676            0.554676              0.0           0.0             0.0
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03R_comparison.png            0.508809            0.508809              0.0           0.0             0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04L_comparison.png            0.467894            0.467894              0.0           0.0             0.0
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png            0.448740            0.448740              0.0           0.0             0.0
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05L_comparison.png            0.513906            0.513906              0.0           0.0             0.0
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05R_comparison.png            0.562237            0.562237              0.0           0.0             0.0
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis\plots\delta_iou_by_dataset.png`
