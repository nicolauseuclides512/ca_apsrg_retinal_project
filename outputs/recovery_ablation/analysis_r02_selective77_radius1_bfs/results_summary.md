# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.6661 ± 0.0792 0.4529 ± 0.0937 0.5302 ± 0.0609 0.3629 ± 0.0559 0.9457 ± 0.0070
CHASEDB1       CA-APSRG        28 0.6663 ± 0.0792 0.4529 ± 0.0937 0.5302 ± 0.0609 0.3630 ± 0.0559 0.9457 ± 0.0070
   DRIVE APSRG Baseline        20 0.7733 ± 0.1080 0.4418 ± 0.0628 0.5564 ± 0.0561 0.3873 ± 0.0519 0.9126 ± 0.0136
   DRIVE       CA-APSRG        20 0.7733 ± 0.1080 0.4417 ± 0.0628 0.5563 ± 0.0561 0.3872 ± 0.0520 0.9126 ± 0.0136
   STARE APSRG Baseline        20 0.6921 ± 0.1311 0.5048 ± 0.0942 0.5712 ± 0.0585 0.4020 ± 0.0570 0.9436 ± 0.0109
   STARE       CA-APSRG        20 0.6922 ± 0.1311 0.5048 ± 0.0942 0.5712 ± 0.0585 0.4020 ± 0.0570 0.9436 ± 0.0109
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.000126          -0.000012             0.000026        0.000023                   11                16                     1
   DRIVE        20              0.000039          -0.000127            -0.000091       -0.000085                    2                13                     5
   STARE        20              0.000089          -0.000028             0.000011        0.000011                    2                16                     2
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.666128       0.079220     0.452889    0.093677       0.530184      0.060932  0.362946 0.055874       0.945684      0.007019
CHASEDB1       CA-APSRG        28        0.666254       0.079214     0.452877    0.093686       0.530210      0.060923  0.362969 0.055870       0.945692      0.007016
   DRIVE APSRG Baseline        20        0.773272       0.108023     0.441826    0.062776       0.556378      0.056082  0.387319 0.051935       0.912628      0.013575
   DRIVE       CA-APSRG        20        0.773311       0.108034     0.441699    0.062783       0.556287      0.056123  0.387234 0.051961       0.912621      0.013578
   STARE APSRG Baseline        20        0.692105       0.131071     0.504782    0.094182       0.571164      0.058451  0.401953 0.056982       0.943586      0.010927
   STARE       CA-APSRG        20        0.692194       0.131076     0.504754    0.094198       0.571174      0.058460  0.401964 0.056992       0.943594      0.010916
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                                            comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0240_comparison.png           0.617328           0.617642        0.000314         0.000884      0.000000
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_14R_comparison.png           0.589795           0.590024        0.000228         0.000466      0.000000
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_06R_comparison.png           0.458774           0.458964        0.000191         0.000922      0.000000
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\35_comparison.png           0.589940           0.590085        0.000144         0.001058     -0.000175
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_13R_comparison.png           0.441899           0.442028        0.000129         0.000469      0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_02R_comparison.png           0.383049           0.383159        0.000110         0.000577      0.000000
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0001_comparison.png           0.469866           0.469934        0.000068         0.000166      0.000000
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_07R_comparison.png           0.505535           0.505600        0.000065         0.000225      0.000000
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_07L_comparison.png           0.585182           0.585243        0.000061         0.000187      0.000000
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_09R_comparison.png           0.505222           0.505275        0.000053         0.000094      0.000000
```

## Worst F1 Drops

```text
 dataset  image_id                                                                                                                            comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   DRIVE        37           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\37_comparison.png           0.473931           0.473142       -0.000790        -0.000348     -0.000763
   DRIVE        38           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\38_comparison.png           0.619848           0.619470       -0.000378        -0.000091     -0.000492
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\34_comparison.png           0.494902           0.494577       -0.000325         0.000173     -0.000434
   DRIVE        29           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\29_comparison.png           0.625173           0.624917       -0.000255        -0.000117     -0.000324
   DRIVE        40           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\40_comparison.png           0.585026           0.584797       -0.000229        -0.000060     -0.000280
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_08R_comparison.png           0.486238           0.486039       -0.000198        -0.000081     -0.000213
   STARE    im0255       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0255_comparison.png           0.596198           0.596076       -0.000123         0.000483     -0.000343
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0005_comparison.png           0.459827           0.459781       -0.000047         0.000241     -0.000209
CHASEDB1 Image_13L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_13L_comparison.png           0.539250           0.539250        0.000000         0.000000      0.000000
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_12R_comparison.png           0.557087           0.557087        0.000000         0.000000      0.000000
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                            comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_02R_comparison.png           0.383049           0.383159        0.000110         0.000577      0.000000
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\23_comparison.png           0.402078           0.402078        0.000000         0.000000      0.000000
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_13R_comparison.png           0.441899           0.442028        0.000129         0.000469      0.000000
CHASEDB1 Image_12L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_12L_comparison.png           0.456417           0.456417        0.000000         0.000000      0.000000
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_06R_comparison.png           0.458774           0.458964        0.000191         0.000922      0.000000
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0005_comparison.png           0.459827           0.459781       -0.000047         0.000241     -0.000209
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_02L_comparison.png           0.469689           0.469689        0.000000         0.000000      0.000000
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0001_comparison.png           0.469866           0.469934        0.000068         0.000166      0.000000
   DRIVE        37           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\37_comparison.png           0.473931           0.473142       -0.000790        -0.000348     -0.000763
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_01R_comparison.png           0.482710           0.482710        0.000000         0.000000      0.000000
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                                            comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\35_comparison.png            0.804029            0.805087         0.001058     -0.000175    1.443291e-04
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_06R_comparison.png            0.712700            0.713622         0.000922      0.000000    1.908195e-04
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0240_comparison.png            0.732328            0.733213         0.000884      0.000000    3.139934e-04
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_02R_comparison.png            0.620977            0.621554         0.000577      0.000000    1.096872e-04
   STARE    im0255       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0255_comparison.png            0.782301            0.782784         0.000483     -0.000343   -1.228266e-04
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_13R_comparison.png            0.596445            0.596914         0.000469      0.000000    1.285258e-04
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_14R_comparison.png            0.595867            0.596334         0.000466      0.000000    2.283908e-04
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_04R_comparison.png            0.691911            0.692197         0.000286     -0.000081    6.217957e-07
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\STARE\comparison\im0005_comparison.png            0.534235            0.534476         0.000241     -0.000209   -4.654764e-05
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_07R_comparison.png            0.666801            0.667026         0.000225      0.000000    6.453644e-05
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                            comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        37           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\37_comparison.png            0.758431            0.758083        -0.000348     -0.000763       -0.000790
   DRIVE        29           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\29_comparison.png            0.730423            0.730306        -0.000117     -0.000324       -0.000255
   DRIVE        38           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\38_comparison.png            0.763967            0.763876        -0.000091     -0.000492       -0.000378
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_08R_comparison.png            0.686918            0.686837        -0.000081     -0.000213       -0.000198
   DRIVE        40           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\DRIVE\comparison\40_comparison.png            0.757616            0.757556        -0.000060     -0.000280       -0.000229
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_01L_comparison.png            0.681150            0.681150         0.000000      0.000000        0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_02L_comparison.png            0.630326            0.630326         0.000000      0.000000        0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_01R_comparison.png            0.653726            0.653726         0.000000      0.000000        0.000000
CHASEDB1 Image_13L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_13L_comparison.png            0.657838            0.657838         0.000000      0.000000        0.000000
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r02_selective77_radius1_bfs\CHASEDB1\comparison\Image_12R_comparison.png            0.651071            0.651071         0.000000      0.000000        0.000000
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r02_selective77_radius1_bfs\plots\delta_iou_by_dataset.png`
