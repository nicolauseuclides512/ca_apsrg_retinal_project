# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.4501 ± 0.0498 0.7066 ± 0.0507 0.5469 ± 0.0335 0.3771 ± 0.0322 0.9197 ± 0.0060
CHASEDB1       CA-APSRG        28 0.4552 ± 0.0520 0.7242 ± 0.0485 0.5559 ± 0.0357 0.3858 ± 0.0347 0.9207 ± 0.0058
   DRIVE APSRG Baseline        20 0.7112 ± 0.1099 0.6943 ± 0.0491 0.6970 ± 0.0632 0.5381 ± 0.0687 0.9246 ± 0.0169
   DRIVE       CA-APSRG        20 0.6999 ± 0.1091 0.7073 ± 0.0489 0.6980 ± 0.0643 0.5393 ± 0.0698 0.9236 ± 0.0173
   STARE APSRG Baseline        20 0.5356 ± 0.1401 0.8348 ± 0.0485 0.6413 ± 0.1157 0.4816 ± 0.1197 0.9286 ± 0.0245
   STARE       CA-APSRG        20 0.5244 ± 0.1382 0.8454 ± 0.0464 0.6360 ± 0.1166 0.4760 ± 0.1196 0.9259 ± 0.0255
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.005099           0.017542             0.009027        0.008714                   25                 0                     3
   DRIVE        20             -0.011277           0.013051             0.000981        0.001265                   11                 0                     9
   STARE        20             -0.011153           0.010541            -0.005227       -0.005619                    1                 0                    19
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.450081       0.049781     0.706640    0.050733       0.546873      0.033486  0.377057 0.032215       0.919714      0.005993
CHASEDB1       CA-APSRG        28        0.455179       0.052039     0.724183    0.048505       0.555899      0.035663  0.385771 0.034706       0.920679      0.005772
   DRIVE APSRG Baseline        20        0.711187       0.109914     0.694250    0.049080       0.696985      0.063221  0.538063 0.068692       0.924645      0.016884
   DRIVE       CA-APSRG        20        0.699910       0.109103     0.707301    0.048915       0.697966      0.064336  0.539328 0.069764       0.923590      0.017300
   STARE APSRG Baseline        20        0.535552       0.140052     0.834849    0.048525       0.641263      0.115718  0.481612 0.119730       0.928647      0.024468
   STARE       CA-APSRG        20        0.524400       0.138211     0.845389    0.046401       0.636035      0.116561  0.475994 0.119608       0.925948      0.025545
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                   comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_04R_comparison.png           0.529906           0.547086        0.017180         0.017249      0.015442
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_14L_comparison.png           0.577077           0.591598        0.014521         0.010935      0.021193
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_07R_comparison.png           0.568159           0.582312        0.014153         0.012301      0.016637
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_05L_comparison.png           0.582166           0.595985        0.013819         0.007078      0.024875
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_07L_comparison.png           0.565541           0.578760        0.013219         0.011219      0.016078
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_05R_comparison.png           0.617387           0.630358        0.012971         0.007328      0.021148
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_14R_comparison.png           0.484300           0.496291        0.011990         0.009124      0.017466
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_01R_comparison.png           0.542630           0.554065        0.011435         0.006734      0.020292
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_02R_comparison.png           0.514027           0.525287        0.011259         0.005776      0.020804
CHASEDB1 Image_06L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_06L_comparison.png           0.556411           0.567197        0.010786         0.006228      0.018792
```

## Worst F1 Drops

```text
dataset image_id                                                                                             comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
  STARE   im0162 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0162_comparison.png           0.665469           0.653927       -0.011542        -0.016008      0.006163
  STARE   im0003 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0003_comparison.png           0.525235           0.515781       -0.009454        -0.011918      0.007812
  STARE   im0081 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0081_comparison.png           0.696973           0.687729       -0.009244        -0.015158      0.008066
  STARE   im0319 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0319_comparison.png           0.387167           0.378887       -0.008280        -0.008037      0.016443
  STARE   im0291 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0291_comparison.png           0.422421           0.414937       -0.007484        -0.006790      0.005183
  STARE   im0255 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0255_comparison.png           0.753962           0.746743       -0.007220        -0.017452      0.008284
  STARE   im0044 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0044_comparison.png           0.656001           0.649623       -0.006379        -0.011231      0.008916
  STARE   im0239 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0239_comparison.png           0.708650           0.702920       -0.005730        -0.013635      0.009652
  STARE   im0077 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0077_comparison.png           0.742959           0.737453       -0.005507        -0.012415      0.007277
  STARE   im0002 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0002_comparison.png           0.536134           0.531100       -0.005034        -0.008806      0.011310
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                   comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0319_comparison.png           0.387167           0.378887       -0.008280        -0.008037      0.016443
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0291_comparison.png           0.422421           0.414937       -0.007484        -0.006790      0.005183
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\DRIVE\comparison\23_comparison.png           0.496393           0.493062       -0.003332        -0.008278      0.009026
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_14R_comparison.png           0.484300           0.496291        0.011990         0.009124      0.017466
CHASEDB1 Image_11L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_11L_comparison.png           0.505614           0.504043       -0.001571        -0.004316      0.010720
CHASEDB1 Image_11R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_11R_comparison.png           0.512176           0.513784        0.001608        -0.000834      0.010874
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0003_comparison.png           0.525235           0.515781       -0.009454        -0.011918      0.007812
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_10L_comparison.png           0.508716           0.516048        0.007333         0.002535      0.021206
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_09L_comparison.png           0.519409           0.517554       -0.001855        -0.004505      0.011046
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_02R_comparison.png           0.514027           0.525287        0.011259         0.005776      0.020804
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                   comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_04R_comparison.png            0.448740            0.465988         0.017249      0.015442        0.017180
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_07R_comparison.png            0.483292            0.495593         0.012301      0.016637        0.014153
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_07L_comparison.png            0.474207            0.485426         0.011219      0.016078        0.013219
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_14L_comparison.png            0.464814            0.475749         0.010935      0.021193        0.014521
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_14R_comparison.png            0.363962            0.373086         0.009124      0.017466        0.011990
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_12R_comparison.png            0.477848            0.485318         0.007470      0.014314        0.009949
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_05R_comparison.png            0.562237            0.569565         0.007328      0.021148        0.012971
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_05L_comparison.png            0.513906            0.520984         0.007078      0.024875        0.013819
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_01R_comparison.png            0.457908            0.464642         0.006734      0.020292        0.011435
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\CHASEDB1\comparison\Image_08R_comparison.png            0.435878            0.442260         0.006382      0.020021        0.010735
```

## Worst Precision Drops

```text
dataset image_id                                                                                             comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
  STARE   im0255 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0255_comparison.png            0.690550            0.673098        -0.017452      0.008284       -0.007220
  DRIVE       22     E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\DRIVE\comparison\22_comparison.png            0.740930            0.724713        -0.016217      0.014161       -0.000092
  DRIVE       37     E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\DRIVE\comparison\37_comparison.png            0.710395            0.694180        -0.016215      0.014043       -0.001228
  STARE   im0162 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0162_comparison.png            0.523024            0.507016        -0.016008      0.006163       -0.011542
  DRIVE       21     E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\DRIVE\comparison\21_comparison.png            0.707073            0.691123        -0.015950      0.010832       -0.003891
  STARE   im0081 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0081_comparison.png            0.567412            0.552254        -0.015158      0.008066       -0.009244
  DRIVE       27     E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\DRIVE\comparison\27_comparison.png            0.711558            0.697052        -0.014507      0.015101       -0.000350
  DRIVE       29     E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\DRIVE\comparison\29_comparison.png            0.702134            0.687764        -0.014369      0.012654       -0.001121
  DRIVE       28     E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\DRIVE\comparison\28_comparison.png            0.812493            0.798731        -0.013762      0.014685        0.003354
  STARE   im0239 E:\ca_apsrg_retinal_project\outputs\experiments_exp1_recall_oriented\STARE\comparison\im0239_comparison.png            0.616135            0.602500        -0.013635      0.009652       -0.005730
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\analysis_exp1_recall_oriented\plots\delta_iou_by_dataset.png`
