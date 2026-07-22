# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.6036 ± 0.0689 0.6089 ± 0.0732 0.6015 ± 0.0487 0.4318 ± 0.0498 0.9449 ± 0.0066
CHASEDB1       CA-APSRG        28 0.6036 ± 0.0689 0.6089 ± 0.0732 0.6016 ± 0.0487 0.4318 ± 0.0498 0.9449 ± 0.0066
   DRIVE APSRG Baseline        20 0.6804 ± 0.0733 0.7399 ± 0.0662 0.7056 ± 0.0524 0.5473 ± 0.0575 0.9238 ± 0.0107
   DRIVE       CA-APSRG        20 0.6804 ± 0.0733 0.7398 ± 0.0663 0.7056 ± 0.0525 0.5473 ± 0.0576 0.9238 ± 0.0107
   STARE APSRG Baseline        20 0.5262 ± 0.0629 0.8393 ± 0.0805 0.6434 ± 0.0530 0.4765 ± 0.0575 0.9307 ± 0.0101
   STARE       CA-APSRG        20 0.5262 ± 0.0629 0.8393 ± 0.0805 0.6435 ± 0.0531 0.4765 ± 0.0575 0.9307 ± 0.0101
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.000027          -0.000003             0.000012        0.000012                    6                22                     0
   DRIVE        20              0.000009          -0.000017            -0.000004       -0.000003                    2                17                     1
   STARE        20              0.000034           0.000000             0.000024        0.000028                    4                16                     0
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.603606       0.068885     0.608876    0.073198       0.601543      0.048677  0.431817 0.049787       0.944918      0.006646
CHASEDB1       CA-APSRG        28        0.603633       0.068886     0.608873    0.073202       0.601555      0.048676  0.431829 0.049786       0.944921      0.006646
   DRIVE APSRG Baseline        20        0.680394       0.073316     0.739864    0.066232       0.705564      0.052438  0.547286 0.057548       0.923806      0.010726
   DRIVE       CA-APSRG        20        0.680404       0.073317     0.739847    0.066267       0.705560      0.052458  0.547284 0.057569       0.923807      0.010733
   STARE APSRG Baseline        20        0.526208       0.062899     0.839313    0.080492       0.643445      0.053046  0.476458 0.057504       0.930701      0.010063
   STARE       CA-APSRG        20        0.526243       0.062928     0.839313    0.080492       0.643469      0.053061  0.476486 0.057525       0.930709      0.010061
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0240_comparison.png           0.721842           0.722031        0.000190         0.000299           0.0
   STARE    im0163       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0163_comparison.png           0.699123           0.699252        0.000129         0.000165           0.0
   DRIVE        30           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\DRIVE\comparison\30_comparison.png           0.703700           0.703805        0.000106         0.000200           0.0
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0005_comparison.png           0.627509           0.627604        0.000095         0.000137           0.0
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_14R_comparison.png           0.615635           0.615705        0.000070         0.000119           0.0
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0001_comparison.png           0.575774           0.575843        0.000069         0.000088           0.0
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_13R_comparison.png           0.577108           0.577175        0.000067         0.000135           0.0
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_07R_comparison.png           0.607987           0.608052        0.000065         0.000141           0.0
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_07L_comparison.png           0.634177           0.634235        0.000057         0.000124           0.0
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_09R_comparison.png           0.563133           0.563184        0.000051         0.000072           0.0
```

## Worst F1 Drops

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\DRIVE\comparison\34_comparison.png           0.612983           0.612776       -0.000207        -0.000109     -0.000279
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_01L_comparison.png           0.607613           0.607613        0.000000         0.000000      0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_02L_comparison.png           0.523326           0.523326        0.000000         0.000000      0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_01R_comparison.png           0.616735           0.616735        0.000000         0.000000      0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_03L_comparison.png           0.661511           0.661511        0.000000         0.000000      0.000000
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_03R_comparison.png           0.647570           0.647570        0.000000         0.000000      0.000000
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_04L_comparison.png           0.664398           0.664398        0.000000         0.000000      0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_02R_comparison.png           0.484688           0.484688        0.000000         0.000000      0.000000
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_08R_comparison.png           0.586357           0.586357        0.000000         0.000000      0.000000
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_05R_comparison.png           0.701517           0.701517        0.000000         0.000000      0.000000
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_02R_comparison.png           0.484688           0.484688        0.000000         0.000000      0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_02L_comparison.png           0.523326           0.523326        0.000000         0.000000      0.000000
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\DRIVE\comparison\23_comparison.png           0.526720           0.526720        0.000000         0.000000      0.000000
CHASEDB1 Image_12L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_12L_comparison.png           0.528181           0.528181        0.000000         0.000000      0.000000
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_10L_comparison.png           0.554348           0.554348        0.000000         0.000000      0.000000
   STARE    im0324       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0324_comparison.png           0.562486           0.562486        0.000000         0.000000      0.000000
CHASEDB1 Image_09R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_09R_comparison.png           0.563133           0.563184        0.000051         0.000072      0.000000
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_04R_comparison.png           0.566993           0.567009        0.000016         0.000173     -0.000081
   STARE    im0003       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0003_comparison.png           0.567748           0.567748        0.000000         0.000000      0.000000
   STARE    im0002       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0002_comparison.png           0.573116           0.573116        0.000000         0.000000      0.000000
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   STARE    im0240       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0240_comparison.png            0.640867            0.641166         0.000299      0.000000        0.000190
   DRIVE        30           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\DRIVE\comparison\30_comparison.png            0.683815            0.684015         0.000200      0.000000        0.000106
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_04R_comparison.png            0.642605            0.642777         0.000173     -0.000081        0.000016
   STARE    im0163       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0163_comparison.png            0.560407            0.560573         0.000165      0.000000        0.000129
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_07R_comparison.png            0.633164            0.633305         0.000141      0.000000        0.000065
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\STARE\comparison\im0005_comparison.png            0.534217            0.534355         0.000137      0.000000        0.000095
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_13R_comparison.png            0.579053            0.579188         0.000135      0.000000        0.000067
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_07L_comparison.png            0.659558            0.659682         0.000124      0.000000        0.000057
CHASEDB1 Image_14R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_14R_comparison.png            0.566289            0.566408         0.000119      0.000000        0.000070
   DRIVE        27           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\DRIVE\comparison\27_comparison.png            0.673869            0.673969         0.000099     -0.000069        0.000029
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\DRIVE\comparison\34_comparison.png            0.658451            0.658341        -0.000109     -0.000279       -0.000207
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_01L_comparison.png            0.610377            0.610377         0.000000      0.000000        0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_02L_comparison.png            0.603312            0.603312         0.000000      0.000000        0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_01R_comparison.png            0.613862            0.613862         0.000000      0.000000        0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_03L_comparison.png            0.708328            0.708328         0.000000      0.000000        0.000000
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_03R_comparison.png            0.675184            0.675184         0.000000      0.000000        0.000000
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_04L_comparison.png            0.658755            0.658755         0.000000      0.000000        0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_02R_comparison.png            0.519214            0.519214         0.000000      0.000000        0.000000
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_08R_comparison.png            0.605774            0.605774         0.000000      0.000000        0.000000
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r04_local_or_region\CHASEDB1\comparison\Image_05R_comparison.png            0.719298            0.719298         0.000000      0.000000        0.000000
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r04_local_or_region\plots\delta_iou_by_dataset.png`
