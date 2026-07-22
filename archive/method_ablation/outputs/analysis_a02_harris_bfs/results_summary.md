# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.7249 ± 0.1205 0.1437 ± 0.1318 0.2145 ± 0.1546 0.1290 ± 0.1063 0.9361 ± 0.0114
CHASEDB1       CA-APSRG        28 0.7249 ± 0.1205 0.1436 ± 0.1317 0.2145 ± 0.1545 0.1289 ± 0.1062 0.9361 ± 0.0114
   DRIVE APSRG Baseline        20 0.8267 ± 0.1473 0.2939 ± 0.1285 0.4200 ± 0.1505 0.2762 ± 0.1151 0.9050 ± 0.0142
   DRIVE       CA-APSRG        20 0.8266 ± 0.1473 0.2935 ± 0.1284 0.4195 ± 0.1505 0.2758 ± 0.1151 0.9050 ± 0.0143
   STARE APSRG Baseline        20 0.6328 ± 0.2985 0.3195 ± 0.2137 0.4044 ± 0.2412 0.2789 ± 0.1778 0.9408 ± 0.0114
   STARE       CA-APSRG        20 0.6329 ± 0.2986 0.3194 ± 0.2136 0.4044 ± 0.2412 0.2788 ± 0.1778 0.9408 ± 0.0114
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28             -0.000021          -0.000051            -0.000046       -0.000042                    0                25                     3
   DRIVE        20             -0.000103          -0.000426            -0.000474       -0.000394                    0                 7                    13
   STARE        20              0.000101          -0.000101            -0.000036       -0.000036                    4                13                     3
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.724880       0.120534     0.143660    0.131787       0.214504      0.154575  0.128975 0.106250       0.936106      0.011360
CHASEDB1       CA-APSRG        28        0.724859       0.120542     0.143608    0.131673       0.214459      0.154482  0.128933 0.106160       0.936103      0.011355
   DRIVE APSRG Baseline        20        0.826712       0.147302     0.293910    0.128517       0.419952      0.150534  0.276165 0.115145       0.905046      0.014242
   DRIVE       CA-APSRG        20        0.826610       0.147258     0.293485    0.128418       0.419479      0.150474  0.275772 0.115065       0.904993      0.014257
   STARE APSRG Baseline        20        0.632793       0.298522     0.319524    0.213669       0.404403      0.241236  0.278874 0.177783       0.940760      0.011355
   STARE       CA-APSRG        20        0.632894       0.298559     0.319423    0.213575       0.404368      0.241207  0.278839 0.177752       0.940763      0.011358
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                             comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0081       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0081_comparison.png           0.655702           0.655891        0.000189         0.000388      0.000000
   STARE    im0044       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0044_comparison.png           0.598377           0.598513        0.000137         0.000357      0.000000
   STARE    im0139       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0139_comparison.png           0.627600           0.627732        0.000132         0.000795     -0.000235
   STARE    im0235       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0235_comparison.png           0.603563           0.603664        0.000101         0.000375      0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_02R_comparison.png           0.077906           0.077906        0.000000         0.000000      0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_02L_comparison.png           0.109886           0.109886        0.000000         0.000000      0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_01R_comparison.png           0.076110           0.076110        0.000000         0.000000      0.000000
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_01L_comparison.png           0.195662           0.195662        0.000000         0.000000      0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_03L_comparison.png           0.279021           0.279021        0.000000         0.000000      0.000000
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_03R_comparison.png           0.278005           0.278005        0.000000         0.000000      0.000000
```

## Worst F1 Drops

```text
 dataset  image_id                                                                                                             comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\34_comparison.png           0.307626           0.306132       -0.001493        -0.000440     -0.001084
   DRIVE        38           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\38_comparison.png           0.317117           0.315756       -0.001361        -0.000504     -0.000983
   DRIVE        21           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\21_comparison.png           0.461128           0.460241       -0.000887        -0.000201     -0.000771
   STARE    im0239       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0239_comparison.png           0.625166           0.624306       -0.000860        -0.000181     -0.001094
   DRIVE        36           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\36_comparison.png           0.531813           0.530990       -0.000823        -0.000243     -0.000808
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\35_comparison.png           0.354191           0.353400       -0.000791        -0.000192     -0.000594
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_09L_comparison.png           0.522152           0.521384       -0.000768        -0.000380     -0.000845
   DRIVE        25           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\25_comparison.png           0.600766           0.600079       -0.000687        -0.000267     -0.000790
   DRIVE        39           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\39_comparison.png           0.564646           0.563966       -0.000680        -0.000210     -0.000741
   DRIVE        26           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\26_comparison.png           0.535642           0.534964       -0.000678         0.000374     -0.000873
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                             comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0291       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0291_comparison.png           0.000000           0.000000             0.0              0.0           0.0
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0001_comparison.png           0.007986           0.007986             0.0              0.0           0.0
   STARE    im0002       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0002_comparison.png           0.025576           0.025576             0.0              0.0           0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_04L_comparison.png           0.042828           0.042828             0.0              0.0           0.0
CHASEDB1 Image_10L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_10L_comparison.png           0.045822           0.045822             0.0              0.0           0.0
   STARE    im0324       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0324_comparison.png           0.048480           0.048480             0.0              0.0           0.0
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_13R_comparison.png           0.056774           0.056774             0.0              0.0           0.0
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_06R_comparison.png           0.062870           0.062870             0.0              0.0           0.0
CHASEDB1 Image_13L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_13L_comparison.png           0.065331           0.065331             0.0              0.0           0.0
CHASEDB1 Image_06L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_06L_comparison.png           0.071754           0.071754             0.0              0.0           0.0
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                             comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   STARE    im0139       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0139_comparison.png            0.737453            0.738248         0.000795     -0.000235        0.000132
   STARE    im0081       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0081_comparison.png            0.664072            0.664460         0.000388      0.000000        0.000189
   STARE    im0235       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0235_comparison.png            0.820945            0.821319         0.000375      0.000000        0.000101
   DRIVE        26           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\26_comparison.png            0.790684            0.791059         0.000374     -0.000873       -0.000678
   STARE    im0044       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0044_comparison.png            0.683111            0.683468         0.000357      0.000000        0.000137
   STARE    im0236       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0236_comparison.png            0.829562            0.829831         0.000268     -0.000261       -0.000145
   DRIVE        22           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\22_comparison.png            0.846400            0.846458         0.000058     -0.000235       -0.000247
   STARE    im0162       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0162_comparison.png            0.638333            0.638350         0.000017     -0.000431       -0.000264
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_02R_comparison.png            0.724219            0.724219         0.000000      0.000000        0.000000
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_02L_comparison.png            0.777065            0.777065         0.000000      0.000000        0.000000
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                             comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        38           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\38_comparison.png            0.889302            0.888799        -0.000504     -0.000983       -0.001361
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\34_comparison.png            0.863162            0.862723        -0.000440     -0.001084       -0.001493
CHASEDB1 Image_09L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\CHASEDB1\comparison\Image_09L_comparison.png            0.697092            0.696712        -0.000380     -0.000845       -0.000768
   DRIVE        25           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\25_comparison.png            0.794452            0.794185        -0.000267     -0.000790       -0.000687
   DRIVE        36           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\36_comparison.png            0.867116            0.866873        -0.000243     -0.000808       -0.000823
   DRIVE        39           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\39_comparison.png            0.810036            0.809826        -0.000210     -0.000741       -0.000680
   DRIVE        21           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\21_comparison.png            0.911782            0.911581        -0.000201     -0.000771       -0.000887
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\35_comparison.png            0.923678            0.923486        -0.000192     -0.000594       -0.000791
   STARE    im0239       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\STARE\comparison\im0239_comparison.png            0.793280            0.793099        -0.000181     -0.001094       -0.000860
   DRIVE        40           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a02_harris_bfs\DRIVE\comparison\40_comparison.png            0.876594            0.876455        -0.000139     -0.000440       -0.000476
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a02_harris_bfs\plots\delta_iou_by_dataset.png`
