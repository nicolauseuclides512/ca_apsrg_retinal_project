# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.4501 ± 0.0498 0.7066 ± 0.0507 0.5469 ± 0.0335 0.3771 ± 0.0322 0.9197 ± 0.0060
CHASEDB1       CA-APSRG        28 0.4664 ± 0.0542 0.7046 ± 0.0515 0.5578 ± 0.0349 0.3875 ± 0.0341 0.9235 ± 0.0054
   DRIVE APSRG Baseline        20 0.7112 ± 0.1099 0.6943 ± 0.0491 0.6970 ± 0.0632 0.5381 ± 0.0687 0.9246 ± 0.0169
   DRIVE       CA-APSRG        20 0.7132 ± 0.1090 0.6926 ± 0.0494 0.6972 ± 0.0628 0.5383 ± 0.0682 0.9249 ± 0.0166
   STARE APSRG Baseline        20 0.5356 ± 0.1401 0.8348 ± 0.0485 0.6413 ± 0.1157 0.4816 ± 0.1197 0.9286 ± 0.0245
   STARE       CA-APSRG        20 0.5401 ± 0.1355 0.8343 ± 0.0486 0.6454 ± 0.1102 0.4853 ± 0.1155 0.9304 ± 0.0221
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.016319          -0.002083             0.010908        0.010490                   28                 0                     0
   DRIVE        20              0.001994          -0.001603             0.000259        0.000264                   11                 0                     9
   STARE        20              0.004585          -0.000528             0.004113        0.003720                   20                 0                     0
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.450081       0.049781     0.706640    0.050733       0.546873      0.033486  0.377057 0.032215       0.919714      0.005993
CHASEDB1       CA-APSRG        28        0.466399       0.054156     0.704557    0.051471       0.557781      0.034948  0.387548 0.034087       0.923453      0.005439
   DRIVE APSRG Baseline        20        0.711187       0.109914     0.694250    0.049080       0.696985      0.063221  0.538063 0.068692       0.924645      0.016884
   DRIVE       CA-APSRG        20        0.713181       0.109034     0.692647    0.049355       0.697244      0.062834  0.538327 0.068201       0.924938      0.016637
   STARE APSRG Baseline        20        0.535552       0.140052     0.834849    0.048525       0.641263      0.115718  0.481612 0.119730       0.928647      0.024468
   STARE       CA-APSRG        20        0.540137       0.135509     0.834321    0.048625       0.645376      0.110231  0.485333 0.115545       0.930386      0.022052
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                 comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0319_comparison.png           0.387167           0.419954        0.032788         0.027915     -0.001535
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_04R_comparison.png           0.529906           0.549819        0.019914         0.031335     -0.003644
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_07L_comparison.png           0.565541           0.584443        0.018902         0.028167     -0.001888
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_14L_comparison.png           0.577077           0.594439        0.017362         0.023187     -0.000576
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_14R_comparison.png           0.484300           0.501517        0.017217         0.020325     -0.001854
   STARE    im0004       E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0004_comparison.png           0.535722           0.552765        0.017043         0.022016     -0.002612
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_07R_comparison.png           0.568159           0.584901        0.016743         0.026762     -0.003687
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_01R_comparison.png           0.542630           0.556556        0.013926         0.021552     -0.002622
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_12R_comparison.png           0.574906           0.587583        0.012677         0.019430     -0.003476
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_05R_comparison.png           0.617387           0.629641        0.012254         0.021652     -0.001359
```

## Worst F1 Drops

```text
dataset image_id                                                                                       comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
  DRIVE       28 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\28_comparison.png           0.722088           0.720444       -0.001644         0.000117     -0.002732
  DRIVE       39 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\39_comparison.png           0.734102           0.732545       -0.001557        -0.000035     -0.002928
  DRIVE       40 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\40_comparison.png           0.758027           0.757163       -0.000864         0.001015     -0.002640
  DRIVE       38 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\38_comparison.png           0.751165           0.750464       -0.000701         0.000200     -0.001580
  DRIVE       22 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\22_comparison.png           0.710179           0.709761       -0.000418         0.000678     -0.001342
  DRIVE       33 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\33_comparison.png           0.734866           0.734467       -0.000399         0.001292     -0.001799
  DRIVE       23 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\23_comparison.png           0.496393           0.496082       -0.000311         0.001075     -0.003454
  DRIVE       36 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\36_comparison.png           0.716278           0.716171       -0.000108         0.000044     -0.000195
  DRIVE       24 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\24_comparison.png           0.713424           0.713320       -0.000104         0.000124     -0.000209
  DRIVE       32 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\32_comparison.png           0.729993           0.729996        0.000004         0.001111     -0.000890
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                 comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0319_comparison.png           0.387167           0.419954        0.032788         0.027915     -0.001535
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0291_comparison.png           0.422421           0.431469        0.009048         0.007988     -0.002428
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\23_comparison.png           0.496393           0.496082       -0.000311         0.001075     -0.003454
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_14R_comparison.png           0.484300           0.501517        0.017217         0.020325     -0.001854
CHASEDB1 Image_11L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_11L_comparison.png           0.505614           0.508799        0.003185         0.003728     -0.000606
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_10L_comparison.png           0.508716           0.514286        0.005570         0.007114     -0.001415
CHASEDB1 Image_11R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_11R_comparison.png           0.512176           0.517612        0.005436         0.006210     -0.000411
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_09L_comparison.png           0.519409           0.522572        0.003163         0.003662     -0.000783
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_02R_comparison.png           0.514027           0.524535        0.010507         0.018109     -0.003445
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0003_comparison.png           0.525235           0.525677        0.000442         0.000847     -0.001578
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                 comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_04R_comparison.png            0.448740            0.480075         0.031335     -0.003644        0.019914
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_07L_comparison.png            0.474207            0.502373         0.028167     -0.001888        0.018902
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0319_comparison.png            0.248842            0.276757         0.027915     -0.001535        0.032788
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_07R_comparison.png            0.483292            0.510054         0.026762     -0.003687        0.016743
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_14L_comparison.png            0.464814            0.488001         0.023187     -0.000576        0.017362
   STARE    im0004       E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0004_comparison.png            0.417797            0.439813         0.022016     -0.002612        0.017043
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_05R_comparison.png            0.562237            0.583889         0.021652     -0.001359        0.012254
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_01R_comparison.png            0.457908            0.479459         0.021552     -0.002622        0.013926
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_05L_comparison.png            0.513906            0.534273         0.020368     -0.001738        0.012164
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\CHASEDB1\comparison\Image_14R_comparison.png            0.363962            0.384288         0.020325     -0.001854        0.017217
```

## Worst Precision Drops

```text
dataset image_id                                                                                           comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
  DRIVE       39     E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\39_comparison.png            0.752799            0.752764        -0.000035     -0.002928       -0.001557
  DRIVE       36     E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\36_comparison.png            0.822041            0.822085         0.000044     -0.000195       -0.000108
  DRIVE       28     E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\28_comparison.png            0.812493            0.812610         0.000117     -0.002732       -0.001644
  DRIVE       24     E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\24_comparison.png            0.869685            0.869809         0.000124     -0.000209       -0.000104
  DRIVE       38     E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\38_comparison.png            0.755461            0.755661         0.000200     -0.001580       -0.000701
  STARE   im0235 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0235_comparison.png            0.681916            0.682198         0.000282      0.000000        0.000170
  STARE   im0163 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0163_comparison.png            0.710241            0.710705         0.000464      0.000000        0.000289
  STARE   im0162 E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\STARE\comparison\im0162_comparison.png            0.523024            0.523546         0.000522     -0.000232        0.000361
  DRIVE       27     E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\27_comparison.png            0.711558            0.712171         0.000612     -0.000206        0.000212
  DRIVE       22     E:\ca_apsrg_retinal_project\outputs\experiments_exp3_balanced_main\DRIVE\comparison\22_comparison.png            0.740930            0.741608         0.000678     -0.001342       -0.000418
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp3_balanced_main\plots\delta_iou_by_dataset.png`
