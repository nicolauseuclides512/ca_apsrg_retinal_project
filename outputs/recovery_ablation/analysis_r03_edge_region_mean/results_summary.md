# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.6722 ± 0.1155 0.1850 ± 0.0512 0.2837 ± 0.0577 0.1666 ± 0.0396 0.9365 ± 0.0089
CHASEDB1       CA-APSRG        28 0.6722 ± 0.1154 0.1850 ± 0.0512 0.2837 ± 0.0577 0.1666 ± 0.0396 0.9365 ± 0.0089
   DRIVE APSRG Baseline        20 0.8063 ± 0.1592 0.1945 ± 0.0609 0.3063 ± 0.0722 0.1830 ± 0.0528 0.8915 ± 0.0182
   DRIVE       CA-APSRG        20 0.8064 ± 0.1595 0.1941 ± 0.0610 0.3058 ± 0.0724 0.1827 ± 0.0529 0.8915 ± 0.0182
   STARE APSRG Baseline        20 0.7849 ± 0.2186 0.2103 ± 0.1151 0.3108 ± 0.0917 0.1875 ± 0.0673 0.9327 ± 0.0155
   STARE       CA-APSRG        20 0.7851 ± 0.2184 0.2103 ± 0.1151 0.3109 ± 0.0917 0.1875 ± 0.0673 0.9327 ± 0.0154
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.000034          -0.000007         8.644492e-08    2.813739e-07                    3                23                     2
   DRIVE        20              0.000068          -0.000377        -4.520857e-04   -3.058849e-04                    0                10                    10
   STARE        20              0.000141           0.000000         1.447001e-05    9.114235e-06                    3                17                     0
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.672210       0.115469     0.184986    0.051225       0.283732      0.057696  0.166601 0.039563       0.936523      0.008855
CHASEDB1       CA-APSRG        28        0.672245       0.115442     0.184979    0.051219       0.283732      0.057701  0.166601 0.039566       0.936524      0.008856
   DRIVE APSRG Baseline        20        0.806283       0.159223     0.194503    0.060922       0.306298      0.072250  0.182980 0.052762       0.891536      0.018226
   DRIVE       CA-APSRG        20        0.806351       0.159513     0.194125    0.060982       0.305846      0.072433  0.182674 0.052870       0.891515      0.018235
   STARE APSRG Baseline        20        0.784940       0.218600     0.210343    0.115076       0.310836      0.091728  0.187478 0.067259       0.932694      0.015460
   STARE       CA-APSRG        20        0.785080       0.218416     0.210343    0.115076       0.310850      0.091712  0.187487 0.067250       0.932703      0.015445
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                                     comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0240_comparison.png           0.279088           0.279211        0.000123         0.001434           0.0
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_14R_comparison.png           0.351326           0.351447        0.000121         0.000542           0.0
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0001_comparison.png           0.168463           0.168554        0.000092         0.000649           0.0
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0005_comparison.png           0.168690           0.168765        0.000075         0.000727           0.0
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_07L_comparison.png           0.387168           0.387218        0.000050         0.000357           0.0
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_09R_comparison.png           0.356250           0.356299        0.000048         0.000155           0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_01R_comparison.png           0.228762           0.228762        0.000000         0.000000           0.0
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_01L_comparison.png           0.237623           0.237623        0.000000         0.000000           0.0
   STARE    im0163       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0163_comparison.png           0.354716           0.354716        0.000000         0.000000           0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_02R_comparison.png           0.185091           0.185091        0.000000         0.000000           0.0
```

## Worst F1 Drops

```text
dataset image_id                                                                                                           comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
  DRIVE       23 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\23_comparison.png           0.227367           0.225321       -0.002046        -0.002441     -0.001612
  DRIVE       34 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\34_comparison.png           0.251954           0.250244       -0.001710        -0.000676     -0.001332
  DRIVE       37 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\37_comparison.png           0.250628           0.249197       -0.001431         0.000269     -0.001040
  DRIVE       35 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\35_comparison.png           0.281653           0.280529       -0.001125         0.002257     -0.000979
  DRIVE       27 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\27_comparison.png           0.385807           0.384998       -0.000809         0.000494     -0.000826
  DRIVE       40 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\40_comparison.png           0.309351           0.308779       -0.000572        -0.000360     -0.000440
  DRIVE       30 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\30_comparison.png           0.367697           0.367217       -0.000480         0.001724     -0.000618
  DRIVE       22 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\22_comparison.png           0.362360           0.362035       -0.000325        -0.000233     -0.000268
  DRIVE       28 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\28_comparison.png           0.324783           0.324467       -0.000316        -0.000001     -0.000248
  DRIVE       24 E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\24_comparison.png           0.282688           0.282459       -0.000229         0.000327     -0.000183
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                     comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0001_comparison.png           0.168463           0.168554        0.000092         0.000649      0.000000
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0005_comparison.png           0.168690           0.168765        0.000075         0.000727      0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_02R_comparison.png           0.185091           0.185091        0.000000         0.000000      0.000000
CHASEDB1 Image_10R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_10R_comparison.png           0.194575           0.194575        0.000000         0.000000      0.000000
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_06R_comparison.png           0.197450           0.197450        0.000000         0.000000      0.000000
   STARE    im0255       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0255_comparison.png           0.206470           0.206470        0.000000         0.000000      0.000000
   DRIVE        36           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\36_comparison.png           0.209555           0.209555        0.000000         0.000000      0.000000
   DRIVE        38           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\38_comparison.png           0.211234           0.211234        0.000000         0.000000      0.000000
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\23_comparison.png           0.227367           0.225321       -0.002046        -0.002441     -0.001612
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_01R_comparison.png           0.228762           0.228762        0.000000         0.000000      0.000000
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                                     comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\35_comparison.png            0.741503            0.743759         0.002257     -0.000979       -0.001125
   DRIVE        30           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\30_comparison.png            0.734097            0.735821         0.001724     -0.000618       -0.000480
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0240_comparison.png            0.673599            0.675033         0.001434      0.000000        0.000123
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0005_comparison.png            0.371068            0.371795         0.000727      0.000000        0.000075
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\STARE\comparison\im0001_comparison.png            0.317033            0.317683         0.000649      0.000000        0.000092
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_14R_comparison.png            0.525809            0.526351         0.000542      0.000000        0.000121
   DRIVE        27           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\27_comparison.png            0.714472            0.714966         0.000494     -0.000826       -0.000809
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_07L_comparison.png            0.733841            0.734198         0.000357      0.000000        0.000050
   DRIVE        24           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\24_comparison.png            0.804914            0.805241         0.000327     -0.000183       -0.000229
   DRIVE        37           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\37_comparison.png            0.751039            0.751308         0.000269     -0.001040       -0.001431
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                     comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\23_comparison.png            0.399029            0.396588        -0.002441     -0.001612       -0.002046
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\34_comparison.png            0.589026            0.588350        -0.000676     -0.001332       -0.001710
   DRIVE        40           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\40_comparison.png            0.707404            0.707045        -0.000360     -0.000440       -0.000572
   DRIVE        22           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\22_comparison.png            0.694458            0.694225        -0.000233     -0.000268       -0.000325
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_12R_comparison.png            0.601663            0.601556        -0.000107     -0.000113       -0.000131
   DRIVE        28           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\DRIVE\comparison\28_comparison.png            0.798856            0.798855        -0.000001     -0.000248       -0.000316
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_04L_comparison.png            0.667902            0.667902         0.000000      0.000000        0.000000
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_01L_comparison.png            0.573768            0.573768         0.000000      0.000000        0.000000
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_07R_comparison.png            0.681044            0.681044         0.000000      0.000000        0.000000
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r03_edge_region_mean\CHASEDB1\comparison\Image_05R_comparison.png            0.802926            0.802926         0.000000      0.000000        0.000000
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r03_edge_region_mean\plots\delta_iou_by_dataset.png`
