# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\experiments\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.4501 ± 0.0498 0.7066 ± 0.0507 0.5469 ± 0.0335 0.3771 ± 0.0322 0.9197 ± 0.0060
CHASEDB1       CA-APSRG        28 0.4977 ± 0.0615 0.6886 ± 0.0546 0.5734 ± 0.0361 0.4029 ± 0.0359 0.9299 ± 0.0052
   DRIVE APSRG Baseline        20 0.7112 ± 0.1099 0.6943 ± 0.0491 0.6970 ± 0.0632 0.5381 ± 0.0687 0.9246 ± 0.0169
   DRIVE       CA-APSRG        20 0.7351 ± 0.1113 0.6465 ± 0.0499 0.6824 ± 0.0603 0.5207 ± 0.0636 0.9249 ± 0.0158
   STARE APSRG Baseline        20 0.5356 ± 0.1401 0.8348 ± 0.0485 0.6413 ± 0.1157 0.4816 ± 0.1197 0.9286 ± 0.0245
   STARE       CA-APSRG        20 0.5632 ± 0.1329 0.8098 ± 0.0486 0.6543 ± 0.1005 0.4938 ± 0.1072 0.9355 ± 0.0182
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.047625          -0.018085             0.026573        0.025796                   28                 0                     0
   DRIVE        20              0.023949          -0.047733            -0.014547       -0.017350                    3                 0                    17
   STARE        20              0.027693          -0.025048             0.013031        0.012182                   17                 0                     3
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.450081       0.049781     0.706640    0.050733       0.546873      0.033486  0.377057 0.032215       0.919714      0.005993
CHASEDB1       CA-APSRG        28        0.497706       0.061534     0.688556    0.054612       0.573446      0.036052  0.402853 0.035868       0.929861      0.005158
   DRIVE APSRG Baseline        20        0.711187       0.109914     0.694250    0.049080       0.696985      0.063221  0.538063 0.068692       0.924645      0.016884
   DRIVE       CA-APSRG        20        0.735135       0.111280     0.646517    0.049945       0.682438      0.060261  0.520713 0.063559       0.924912      0.015751
   STARE APSRG Baseline        20        0.535552       0.140052     0.834849    0.048525       0.641263      0.115718  0.481612 0.119730       0.928647      0.024468
   STARE       CA-APSRG        20        0.563245       0.132938     0.809800    0.048604       0.654293      0.100465  0.493795 0.107209       0.935484      0.018198
```

## Best F1 Improvements

```text
 dataset  image_id                                                                              comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0319_comparison.png           0.387167           0.451899        0.064732         0.057981     -0.014525
   STARE    im0004       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0004_comparison.png           0.535722           0.590230        0.054508         0.081355     -0.024431
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0291_comparison.png           0.422421           0.462903        0.040482         0.037044     -0.012980
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14L_comparison.png           0.577077           0.616744        0.039667         0.062180     -0.017497
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png           0.529906           0.569097        0.039192         0.072692     -0.020562
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14R_comparison.png           0.484300           0.520910        0.036610         0.049072     -0.018464
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07L_comparison.png           0.565541           0.601813        0.036272         0.063623     -0.017376
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07R_comparison.png           0.568159           0.602160        0.034001         0.065384     -0.021982
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_12R_comparison.png           0.574906           0.606380        0.031475         0.054264     -0.016697
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png           0.542630           0.573346        0.030716         0.059096     -0.022351
```

## Worst F1 Drops

```text
dataset image_id                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
  DRIVE       36 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\36_comparison.png           0.716278           0.685751       -0.030528         0.013595     -0.053171
  DRIVE       28 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\28_comparison.png           0.722088           0.695636       -0.026452         0.021963     -0.053370
  DRIVE       40 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\40_comparison.png           0.758027           0.731825       -0.026202         0.021223     -0.066120
  DRIVE       35 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\35_comparison.png           0.750274           0.727167       -0.023107         0.020493     -0.053474
  DRIVE       37 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\37_comparison.png           0.706096           0.683952       -0.022144         0.018909     -0.057938
  DRIVE       24 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\24_comparison.png           0.713424           0.691528       -0.021896         0.012902     -0.036295
  DRIVE       34 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\34_comparison.png           0.615991           0.594554       -0.021436         0.013753     -0.051290
  DRIVE       39 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\39_comparison.png           0.734102           0.713525       -0.020578         0.021738     -0.054889
  DRIVE       33 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\33_comparison.png           0.734866           0.715464       -0.019402         0.027258     -0.053900
  DRIVE       38 E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\38_comparison.png           0.751165           0.733206       -0.017959         0.021252     -0.052604
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                              comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0319_comparison.png           0.387167           0.451899        0.064732         0.057981     -0.014525
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0291_comparison.png           0.422421           0.462903        0.040482         0.037044     -0.012980
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\23_comparison.png           0.496393           0.480240       -0.016153         0.003450     -0.055586
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14R_comparison.png           0.484300           0.520910        0.036610         0.049072     -0.018464
CHASEDB1 Image_11L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_11L_comparison.png           0.505614           0.521190        0.015576         0.020833     -0.011346
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_10L_comparison.png           0.508716           0.526438        0.017722         0.027124     -0.016363
CHASEDB1 Image_11R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_11R_comparison.png           0.512176           0.530383        0.018207         0.023279     -0.009270
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0003_comparison.png           0.525235           0.533588        0.008353         0.015214     -0.023949
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_09L_comparison.png           0.519409           0.535702        0.016293         0.020586     -0.009500
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png           0.514027           0.536169        0.022141         0.051062     -0.024449
```

## Best Precision Improvements

```text
 dataset  image_id                                                                              comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   STARE    im0004       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0004_comparison.png            0.417797            0.499152         0.081355     -0.024431        0.054508
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png            0.448740            0.521431         0.072692     -0.020562        0.039192
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05L_comparison.png            0.513906            0.579667         0.065762     -0.022781        0.030014
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07R_comparison.png            0.483292            0.548676         0.065384     -0.021982        0.034001
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07L_comparison.png            0.474207            0.537830         0.063623     -0.017376        0.036272
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05R_comparison.png            0.562237            0.625184         0.062947     -0.020389        0.026689
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14L_comparison.png            0.464814            0.526994         0.062180     -0.017497        0.039667
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png            0.457908            0.517004         0.059096     -0.022351        0.030716
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_03R_comparison.png            0.508809            0.566842         0.058033     -0.018613        0.029030
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0319_comparison.png            0.248842            0.306823         0.057981     -0.014525        0.064732
```

## Worst Precision Drops

```text
 dataset  image_id                                                                              comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\23_comparison.png            0.411307            0.414758         0.003450     -0.055586       -0.016153
   DRIVE        24           E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\24_comparison.png            0.869685            0.882587         0.012902     -0.036295       -0.021896
   DRIVE        36           E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\36_comparison.png            0.822041            0.835636         0.013595     -0.053171       -0.030528
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\34_comparison.png            0.624308            0.638061         0.013753     -0.051290       -0.021436
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0003_comparison.png            0.388300            0.403514         0.015214     -0.023949        0.008353
   STARE    im0162       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0162_comparison.png            0.523024            0.538571         0.015548     -0.052618       -0.002549
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_09R_comparison.png            0.391737            0.408111         0.016373     -0.007190        0.013399
   STARE    im0163       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0163_comparison.png            0.710241            0.727090         0.016850     -0.022747        0.001136
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0005_comparison.png            0.564786            0.582500         0.017715     -0.030034        0.000390
   STARE    im0139       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0139_comparison.png            0.565934            0.584079         0.018145     -0.018352        0.006104
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
