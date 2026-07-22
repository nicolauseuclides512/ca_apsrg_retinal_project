# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.6037 ± 0.0688 0.6087 ± 0.0732 0.6015 ± 0.0487 0.4318 ± 0.0498 0.9449 ± 0.0066
CHASEDB1       CA-APSRG        28 0.6037 ± 0.0688 0.6087 ± 0.0732 0.6015 ± 0.0487 0.4318 ± 0.0498 0.9449 ± 0.0067
   DRIVE APSRG Baseline        20 0.6805 ± 0.0730 0.7404 ± 0.0630 0.7061 ± 0.0522 0.5480 ± 0.0575 0.9239 ± 0.0106
   DRIVE       CA-APSRG        20 0.6805 ± 0.0730 0.7404 ± 0.0630 0.7061 ± 0.0523 0.5480 ± 0.0576 0.9239 ± 0.0106
   STARE APSRG Baseline        20 0.5252 ± 0.0635 0.8389 ± 0.0810 0.6424 ± 0.0528 0.4753 ± 0.0572 0.9304 ± 0.0102
   STARE       CA-APSRG        20 0.5253 ± 0.0636 0.8389 ± 0.0810 0.6424 ± 0.0528 0.4754 ± 0.0573 0.9304 ± 0.0102
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.000027          -0.000003             0.000012        0.000012                    6                22                     0
   DRIVE        20              0.000010          -0.000017            -0.000004       -0.000003                    2                17                     1
   STARE        20              0.000035           0.000000             0.000024        0.000028                    4                16                     0
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.603656       0.068815     0.608737    0.073200       0.601512      0.048656  0.431784 0.049769       0.944923      0.006650
CHASEDB1       CA-APSRG        28        0.603684       0.068816     0.608734    0.073204       0.601524      0.048655  0.431796 0.049769       0.944926      0.006650
   DRIVE APSRG Baseline        20        0.680495       0.073035     0.740383    0.062954       0.706129      0.052238  0.547954 0.057534       0.923949      0.010591
   DRIVE       CA-APSRG        20        0.680504       0.073037     0.740366    0.062990       0.706126      0.052257  0.547951 0.057555       0.923950      0.010598
   STARE APSRG Baseline        20        0.525237       0.063548     0.838876    0.080981       0.642421      0.052814  0.475325 0.057229       0.930404      0.010225
   STARE       CA-APSRG        20        0.525272       0.063579     0.838876    0.080981       0.642446      0.052830  0.475353 0.057252       0.930412      0.010224
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0240_comparison.png           0.723486           0.723677        0.000191         0.000303           0.0
   STARE    im0163       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0163_comparison.png           0.698249           0.698378        0.000128         0.000165           0.0
   DRIVE        30           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\DRIVE\comparison\30_comparison.png           0.703090           0.703196        0.000106         0.000201           0.0
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0005_comparison.png           0.629994           0.630090        0.000095         0.000139           0.0
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_14R_comparison.png           0.615635           0.615705        0.000070         0.000119           0.0
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0001_comparison.png           0.575557           0.575627        0.000069         0.000088           0.0
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_13R_comparison.png           0.577282           0.577349        0.000067         0.000135           0.0
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_07R_comparison.png           0.608118           0.608183        0.000065         0.000141           0.0
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_07L_comparison.png           0.634683           0.634740        0.000057         0.000124           0.0
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_09R_comparison.png           0.563044           0.563095        0.000051         0.000073           0.0
```

## Worst F1 Drops

```text
 dataset  image_id                                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\DRIVE\comparison\34_comparison.png           0.612853           0.612646       -0.000207        -0.000109     -0.000279
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_01L_comparison.png           0.607748           0.607748        0.000000         0.000000      0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_02L_comparison.png           0.523161           0.523161        0.000000         0.000000      0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_01R_comparison.png           0.616466           0.616466        0.000000         0.000000      0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_03L_comparison.png           0.661480           0.661480        0.000000         0.000000      0.000000
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_03R_comparison.png           0.647764           0.647764        0.000000         0.000000      0.000000
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_04L_comparison.png           0.663848           0.663848        0.000000         0.000000      0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_02R_comparison.png           0.484878           0.484878        0.000000         0.000000      0.000000
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_08R_comparison.png           0.586335           0.586335        0.000000         0.000000      0.000000
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_05R_comparison.png           0.701369           0.701369        0.000000         0.000000      0.000000
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_02R_comparison.png           0.484878           0.484878        0.000000         0.000000      0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_02L_comparison.png           0.523161           0.523161        0.000000         0.000000      0.000000
CHASEDB1 Image_12L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_12L_comparison.png           0.528517           0.528517        0.000000         0.000000      0.000000
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\DRIVE\comparison\23_comparison.png           0.530131           0.530131        0.000000         0.000000      0.000000
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_10L_comparison.png           0.554620           0.554620        0.000000         0.000000      0.000000
   STARE    im0324       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0324_comparison.png           0.562580           0.562580        0.000000         0.000000      0.000000
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_09R_comparison.png           0.563044           0.563095        0.000051         0.000073      0.000000
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0003_comparison.png           0.565941           0.565941        0.000000         0.000000      0.000000
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_04R_comparison.png           0.566768           0.566785        0.000016         0.000173     -0.000081
   STARE    im0002       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0002_comparison.png           0.572679           0.572679        0.000000         0.000000      0.000000
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                                                    comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0240_comparison.png            0.644182            0.644484         0.000303      0.000000        0.000191
   DRIVE        30           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\DRIVE\comparison\30_comparison.png            0.685292            0.685493         0.000201      0.000000        0.000106
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_04R_comparison.png            0.642658            0.642831         0.000173     -0.000081        0.000016
   STARE    im0163       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0163_comparison.png            0.559695            0.559860         0.000165      0.000000        0.000128
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_07R_comparison.png            0.633158            0.633299         0.000141      0.000000        0.000065
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\STARE\comparison\im0005_comparison.png            0.537633            0.537772         0.000139      0.000000        0.000095
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_13R_comparison.png            0.579170            0.579305         0.000135      0.000000        0.000067
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_07L_comparison.png            0.659762            0.659886         0.000124      0.000000        0.000057
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_14R_comparison.png            0.566339            0.566458         0.000119      0.000000        0.000070
   DRIVE        27           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\DRIVE\comparison\27_comparison.png            0.674502            0.674602         0.000100     -0.000069        0.000029
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                                    comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\DRIVE\comparison\34_comparison.png            0.657661            0.657552        -0.000109     -0.000279       -0.000207
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_01L_comparison.png            0.610938            0.610938         0.000000      0.000000        0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_02L_comparison.png            0.603070            0.603070         0.000000      0.000000        0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_01R_comparison.png            0.613881            0.613881         0.000000      0.000000        0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_03L_comparison.png            0.708640            0.708640         0.000000      0.000000        0.000000
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_03R_comparison.png            0.675491            0.675491         0.000000      0.000000        0.000000
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_04L_comparison.png            0.658265            0.658265         0.000000      0.000000        0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_02R_comparison.png            0.519199            0.519199         0.000000      0.000000        0.000000
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_08R_comparison.png            0.605839            0.605839         0.000000      0.000000        0.000000
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r05_local_or_region_hybrid_priority\CHASEDB1\comparison\Image_05R_comparison.png            0.719744            0.719744         0.000000      0.000000        0.000000
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r05_local_or_region_hybrid_priority\plots\delta_iou_by_dataset.png`
