# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.4739 ± 0.0555 0.6291 ± 0.0611 0.5361 ± 0.0319 0.3669 ± 0.0300 0.9256 ± 0.0044
CHASEDB1       CA-APSRG        28 0.4821 ± 0.0572 0.6280 ± 0.0614 0.5409 ± 0.0324 0.3713 ± 0.0307 0.9271 ± 0.0044
   DRIVE APSRG Baseline        20 0.5630 ± 0.0906 0.5869 ± 0.0417 0.5715 ± 0.0600 0.4023 ± 0.0558 0.8907 ± 0.0122
   DRIVE       CA-APSRG        20 0.6083 ± 0.0981 0.5767 ± 0.0410 0.5887 ± 0.0619 0.4196 ± 0.0582 0.8998 ± 0.0136
   STARE APSRG Baseline        20 0.4164 ± 0.0777 0.6558 ± 0.0622 0.5030 ± 0.0617 0.3381 ± 0.0539 0.9032 ± 0.0099
   STARE       CA-APSRG        20 0.4340 ± 0.0835 0.6547 ± 0.0623 0.5150 ± 0.0640 0.3491 ± 0.0568 0.9079 ± 0.0099
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.008240          -0.001109             0.004751        0.004474                   28                 0                     0
   DRIVE        20              0.045341          -0.010163             0.017210        0.017274                   20                 0                     0
   STARE        20              0.017594          -0.001077             0.011970        0.010984                   20                 0                     0
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.473892       0.055506     0.629145    0.061083       0.536125      0.031874  0.366867 0.030023       0.925557      0.004396
CHASEDB1       CA-APSRG        28        0.482132       0.057194     0.628036    0.061382       0.540876      0.032356  0.371342 0.030681       0.927105      0.004353
   DRIVE APSRG Baseline        20        0.562999       0.090559     0.586905    0.041733       0.571503      0.059961  0.402293 0.055790       0.890750      0.012238
   DRIVE       CA-APSRG        20        0.608340       0.098125     0.576742    0.041029       0.588713      0.061892  0.419567 0.058210       0.899823      0.013626
   STARE APSRG Baseline        20        0.416446       0.077676     0.655757    0.062203       0.503011      0.061694  0.338122 0.053884       0.903197      0.009866
   STARE       CA-APSRG        20        0.434041       0.083541     0.654680    0.062257       0.514980      0.064018  0.349106 0.056785       0.907890      0.009939
```

## Best F1 Improvements

```text
dataset image_id                                                                                                          comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
  STARE   im0236 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0236_comparison.png           0.531197           0.561121        0.029924         0.048218     -0.001486
  DRIVE       30     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\30_comparison.png           0.553130           0.580072        0.026942         0.066698     -0.013989
  DRIVE       25     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\25_comparison.png           0.615253           0.641757        0.026505         0.068815     -0.012475
  DRIVE       21     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\21_comparison.png           0.569479           0.594499        0.025020         0.051532     -0.008398
  DRIVE       32     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\32_comparison.png           0.578719           0.603185        0.024466         0.063416     -0.011537
  DRIVE       33     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\33_comparison.png           0.568863           0.592744        0.023881         0.058883     -0.009820
  STARE   im0162 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0162_comparison.png           0.481682           0.505189        0.023507         0.031268     -0.001822
  DRIVE       27     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\27_comparison.png           0.576084           0.599092        0.023008         0.051283     -0.009976
  DRIVE       35     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\35_comparison.png           0.580186           0.602450        0.022263         0.057219     -0.010240
  DRIVE       29     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\29_comparison.png           0.565768           0.587357        0.021590         0.053471     -0.012834
```

## Worst F1 Drops

```text
 dataset  image_id                                                                                                                comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\34_comparison.png           0.530931           0.532695        0.001764         0.008003     -0.003283
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_02L_comparison.png           0.517998           0.520270        0.002271         0.006009     -0.002506
CHASEDB1 Image_11L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_11L_comparison.png           0.505436           0.508193        0.002756         0.003721     -0.000978
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_02R_comparison.png           0.496286           0.499067        0.002780         0.007041     -0.002457
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\23_comparison.png           0.392697           0.395894        0.003196         0.005726     -0.002303
CHASEDB1 Image_08L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_08L_comparison.png           0.557796           0.561162        0.003366         0.005835     -0.001661
CHASEDB1 Image_11R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_11R_comparison.png           0.520630           0.523997        0.003367         0.004161     -0.000274
CHASEDB1 Image_12L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_12L_comparison.png           0.521563           0.524978        0.003414         0.006507     -0.001029
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0003_comparison.png           0.445036           0.448479        0.003444         0.003986     -0.000039
CHASEDB1 Image_10R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_10R_comparison.png           0.508257           0.511739        0.003482         0.005974     -0.001213
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0319       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0319_comparison.png           0.356082           0.365492        0.009410         0.008670     -0.000658
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\23_comparison.png           0.392697           0.395894        0.003196         0.005726     -0.002303
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0291_comparison.png           0.398605           0.406352        0.007748         0.007104     -0.001634
   STARE    im0004       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0004_comparison.png           0.432768           0.440465        0.007697         0.011067     -0.001561
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0003_comparison.png           0.445036           0.448479        0.003444         0.003986     -0.000039
   STARE    im0324       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0324_comparison.png           0.472750           0.477806        0.005055         0.007014     -0.003008
   DRIVE        31           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\31_comparison.png           0.460727           0.477921        0.017193         0.027226     -0.007539
   STARE    im0002       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0002_comparison.png           0.477202           0.483666        0.006464         0.008914     -0.002836
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_09L_comparison.png           0.492025           0.497101        0.005076         0.005885     -0.000659
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_13R_comparison.png           0.492225           0.497987        0.005763         0.010020     -0.001518
```

## Best Precision Improvements

```text
dataset image_id                                                                                                      comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
  DRIVE       25 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\25_comparison.png            0.608227            0.677043         0.068815     -0.012475        0.026505
  DRIVE       30 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\30_comparison.png            0.530114            0.596812         0.066698     -0.013989        0.026942
  DRIVE       32 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\32_comparison.png            0.571977            0.635393         0.063416     -0.011537        0.024466
  DRIVE       33 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\33_comparison.png            0.557620            0.616503         0.058883     -0.009820        0.023881
  DRIVE       35 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\35_comparison.png            0.574374            0.631593         0.057219     -0.010240        0.022263
  DRIVE       28 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\28_comparison.png            0.644838            0.701162         0.056324     -0.012791        0.015354
  DRIVE       29 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\29_comparison.png            0.539662            0.593133         0.053471     -0.012834        0.021590
  DRIVE       21 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\21_comparison.png            0.525638            0.577170         0.051532     -0.008398        0.025020
  DRIVE       22 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\22_comparison.png            0.561234            0.612621         0.051387     -0.012013        0.018916
  DRIVE       27 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\27_comparison.png            0.540992            0.592275         0.051283     -0.009976        0.023008
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
CHASEDB1 Image_11L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_11L_comparison.png            0.396305            0.400027         0.003721     -0.000978        0.002756
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\STARE\comparison\im0003_comparison.png            0.337415            0.341401         0.003986     -0.000039        0.003444
CHASEDB1 Image_11R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_11R_comparison.png            0.404303            0.408464         0.004161     -0.000274        0.003367
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_09R_comparison.png            0.373872            0.379062         0.005191     -0.001065        0.004456
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\DRIVE\comparison\23_comparison.png            0.331819            0.337545         0.005726     -0.002303        0.003196
CHASEDB1 Image_08L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_08L_comparison.png            0.478098            0.483934         0.005835     -0.001661        0.003366
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_09L_comparison.png            0.368294            0.374180         0.005885     -0.000659        0.005076
CHASEDB1 Image_13L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_13L_comparison.png            0.436932            0.442900         0.005969     -0.000254        0.004293
CHASEDB1 Image_10R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_10R_comparison.png            0.441962            0.447935         0.005974     -0.001213        0.003482
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a03_fuzzy_srg_bfs\CHASEDB1\comparison\Image_02L_comparison.png            0.486602            0.492610         0.006009     -0.002506        0.002271
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a03_fuzzy_srg_bfs\plots\delta_iou_by_dataset.png`
