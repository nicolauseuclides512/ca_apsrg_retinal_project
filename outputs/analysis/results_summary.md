# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\experiments\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.4502 ± 0.0498 0.7071 ± 0.0506 0.5471 ± 0.0335 0.3773 ± 0.0322 0.9197 ± 0.0060
CHASEDB1       CA-APSRG        28 0.4552 ± 0.0520 0.7244 ± 0.0485 0.5560 ± 0.0357 0.3859 ± 0.0347 0.9207 ± 0.0058
   DRIVE APSRG Baseline        20 0.7111 ± 0.1099 0.6943 ± 0.0491 0.6970 ± 0.0632 0.5380 ± 0.0687 0.9246 ± 0.0169
   DRIVE       CA-APSRG        20 0.6999 ± 0.1091 0.7073 ± 0.0489 0.6980 ± 0.0643 0.5393 ± 0.0698 0.9236 ± 0.0173
   STARE APSRG Baseline        20 0.5355 ± 0.1400 0.8349 ± 0.0485 0.6412 ± 0.1157 0.4815 ± 0.1197 0.9286 ± 0.0245
   STARE       CA-APSRG        20 0.5244 ± 0.1382 0.8454 ± 0.0464 0.6360 ± 0.1165 0.4760 ± 0.1196 0.9259 ± 0.0255
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.005056           0.017323             0.008925        0.008619                   25                 0                     3
   DRIVE        20             -0.011183           0.013014             0.001005        0.001294                   12                 0                     8
   STARE        20             -0.011083           0.010503            -0.005188       -0.005574                    1                 0                    19
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.450177       0.049783     0.707067    0.050648       0.547077      0.033489  0.377251 0.032228       0.919731      0.005992
CHASEDB1       CA-APSRG        28        0.455233       0.052040     0.724390    0.048530       0.556001      0.035677  0.385870 0.034725       0.920690      0.005771
   DRIVE APSRG Baseline        20        0.711093       0.109886     0.694287    0.049080       0.696961      0.063216  0.538034 0.068685       0.924632      0.016884
   DRIVE       CA-APSRG        20        0.699910       0.109103     0.707301    0.048915       0.697966      0.064336  0.539328 0.069764       0.923590      0.017300
   STARE APSRG Baseline        20        0.535460       0.140012     0.834896    0.048543       0.641208      0.115697  0.481549 0.119703       0.928626      0.024470
   STARE       CA-APSRG        20        0.524377       0.138201     0.845399    0.046415       0.636019      0.116549  0.475975 0.119595       0.925942      0.025543
```

## Best F1 Improvements

```text
 dataset  image_id                                                                              comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png           0.530185           0.547151        0.016966         0.017150      0.015009
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14L_comparison.png           0.577404           0.591864        0.014460         0.010896      0.021087
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07R_comparison.png           0.568366           0.582536        0.014170         0.012352      0.016583
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05L_comparison.png           0.582501           0.596159        0.013658         0.007030      0.024532
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07L_comparison.png           0.565616           0.579021        0.013405         0.011370      0.016319
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05R_comparison.png           0.617510           0.630441        0.012931         0.007344      0.021025
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14R_comparison.png           0.484616           0.496375        0.011759         0.008971      0.017038
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png           0.542812           0.554129        0.011317         0.006676      0.020058
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png           0.514136           0.525345        0.011209         0.005804      0.020617
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_08R_comparison.png           0.536547           0.547014        0.010467         0.006232      0.019496
```

## Worst F1 Drops

```text
dataset image_id                                                                        comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
  STARE   im0162 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0162_comparison.png           0.665469           0.653804       -0.011665        -0.016156      0.006163
  STARE   im0003 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0003_comparison.png           0.525128           0.515781       -0.009346        -0.011801      0.007812
  STARE   im0081 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0081_comparison.png           0.696905           0.687598       -0.009308        -0.015237      0.008066
  STARE   im0319 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0319_comparison.png           0.387173           0.378887       -0.008286        -0.008006      0.016004
  STARE   im0291 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0291_comparison.png           0.422384           0.414973       -0.007411        -0.006744      0.005369
  STARE   im0255 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0255_comparison.png           0.753818           0.746743       -0.007075        -0.017210      0.008284
  STARE   im0044 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0044_comparison.png           0.655801           0.649623       -0.006178        -0.010973      0.008916
  STARE   im0239 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0239_comparison.png           0.708585           0.702920       -0.005664        -0.013536      0.009652
  STARE   im0077 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0077_comparison.png           0.742959           0.737453       -0.005507        -0.012415      0.007277
  STARE   im0002 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0002_comparison.png           0.536134           0.531100       -0.005034        -0.008806      0.011310
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                              comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0319_comparison.png           0.387173           0.378887       -0.008286        -0.008006      0.016004
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0291_comparison.png           0.422384           0.414973       -0.007411        -0.006744      0.005369
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\23_comparison.png           0.496393           0.493062       -0.003332        -0.008278      0.009026
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14R_comparison.png           0.484616           0.496375        0.011759         0.008971      0.017038
CHASEDB1 Image_11L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_11L_comparison.png           0.505639           0.504195       -0.001444        -0.004210      0.010877
CHASEDB1 Image_11R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_11R_comparison.png           0.512253           0.513784        0.001531        -0.000882      0.010717
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0003_comparison.png           0.525128           0.515781       -0.009346        -0.011801      0.007812
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_10L_comparison.png           0.509134           0.516357        0.007223         0.002505      0.020874
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_09L_comparison.png           0.519381           0.517554       -0.001827        -0.004475      0.011046
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_02R_comparison.png           0.514136           0.525345        0.011209         0.005804      0.020617
```

## Best Precision Improvements

```text
 dataset  image_id                                                                              comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_04R_comparison.png            0.448879            0.466029         0.017150      0.015009        0.016966
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07R_comparison.png            0.483377            0.495729         0.012352      0.016583        0.014170
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_07L_comparison.png            0.474214            0.485584         0.011370      0.016319        0.013405
CHASEDB1 Image_14L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14L_comparison.png            0.465012            0.475908         0.010896      0.021087        0.014460
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_14R_comparison.png            0.364138            0.373109         0.008971      0.017038        0.011759
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_12R_comparison.png            0.478005            0.485376         0.007371      0.014030        0.009787
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05R_comparison.png            0.562267            0.569612         0.007344      0.021025        0.012931
CHASEDB1 Image_05L E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_05L_comparison.png            0.514058            0.521088         0.007030      0.024532        0.013658
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_01R_comparison.png            0.458005            0.464681         0.006676      0.020058        0.011317
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\experiments\CHASEDB1\comparison\Image_08R_comparison.png            0.436027            0.442260         0.006232      0.019496        0.010467
```

## Worst Precision Drops

```text
dataset image_id                                                                        comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
  STARE   im0255 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0255_comparison.png            0.690308            0.673098        -0.017210      0.008284       -0.007075
  STARE   im0162 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0162_comparison.png            0.523024            0.506868        -0.016156      0.006163       -0.011665
  DRIVE       37     E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\37_comparison.png            0.710231            0.694180        -0.016051      0.014008       -0.001164
  DRIVE       21     E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\21_comparison.png            0.707073            0.691123        -0.015950      0.010832       -0.003891
  DRIVE       22     E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\22_comparison.png            0.740282            0.724713        -0.015569      0.014161        0.000206
  STARE   im0081 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0081_comparison.png            0.567322            0.552085        -0.015237      0.008066       -0.009308
  DRIVE       27     E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\27_comparison.png            0.711535            0.697052        -0.014483      0.014929       -0.000422
  DRIVE       29     E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\29_comparison.png            0.701967            0.687764        -0.014203      0.012618       -0.001056
  DRIVE       28     E:\ca_apsrg_retinal_project\outputs\experiments\DRIVE\comparison\28_comparison.png            0.812493            0.798731        -0.013762      0.014685        0.003354
  STARE   im0239 E:\ca_apsrg_retinal_project\outputs\experiments\STARE\comparison\im0239_comparison.png            0.616036            0.602500        -0.013536      0.009652       -0.005664
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
