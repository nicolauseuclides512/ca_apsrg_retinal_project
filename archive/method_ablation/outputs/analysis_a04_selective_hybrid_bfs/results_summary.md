# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.6595 ± 0.0931 0.2947 ± 0.1271 0.3888 ± 0.1090 0.2468 ± 0.0841 0.9397 ± 0.0088
CHASEDB1       CA-APSRG        28 0.6597 ± 0.0932 0.2947 ± 0.1271 0.3888 ± 0.1090 0.2468 ± 0.0841 0.9397 ± 0.0088
   DRIVE APSRG Baseline        20 0.7730 ± 0.1209 0.3435 ± 0.1025 0.4646 ± 0.1068 0.3086 ± 0.0899 0.9042 ± 0.0160
   DRIVE       CA-APSRG        20 0.7731 ± 0.1210 0.3432 ± 0.1024 0.4644 ± 0.1067 0.3084 ± 0.0898 0.9042 ± 0.0160
   STARE APSRG Baseline        20 0.6735 ± 0.1575 0.4228 ± 0.1646 0.4972 ± 0.1438 0.3411 ± 0.1135 0.9399 ± 0.0121
   STARE       CA-APSRG        20 0.6737 ± 0.1576 0.4228 ± 0.1647 0.4972 ± 0.1438 0.3411 ± 0.1135 0.9399 ± 0.0121
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.000112           0.000000             0.000020        0.000016                    7                21                     0
   DRIVE        20              0.000114          -0.000263            -0.000216       -0.000196                    4                 7                     9
   STARE        20              0.000207          -0.000082            -0.000021       -0.000020                    3                12                     5
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.659542       0.093124     0.294703    0.127103       0.388797      0.108994  0.246771 0.084095       0.939710      0.008829
CHASEDB1       CA-APSRG        28        0.659654       0.093193     0.294703    0.127103       0.388817      0.109001  0.246787 0.084100       0.939715      0.008829
   DRIVE APSRG Baseline        20        0.773017       0.120910     0.343470    0.102493       0.464648      0.106835  0.308565 0.089891       0.904221      0.016044
   DRIVE       CA-APSRG        20        0.773131       0.120991     0.343207    0.102367       0.464432      0.106736  0.308369 0.089797       0.904207      0.016028
   STARE APSRG Baseline        20        0.673535       0.157501     0.422837    0.164645       0.497191      0.143844  0.341096 0.113487       0.939896      0.012138
   STARE       CA-APSRG        20        0.673743       0.157647     0.422755    0.164651       0.497170      0.143837  0.341076 0.113482       0.939904      0.012134
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                                       comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0001_comparison.png           0.424373           0.424618        0.000245         0.000810      0.000000
CHASEDB1 Image_06L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_06L_comparison.png           0.487808           0.487942        0.000134         0.000689      0.000000
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\23_comparison.png           0.294977           0.295078        0.000102         0.000284      0.000000
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_07R_comparison.png           0.397964           0.398059        0.000095         0.000639      0.000000
   DRIVE        28           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\28_comparison.png           0.463390           0.463482        0.000092         0.000542      0.000000
   DRIVE        25           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\25_comparison.png           0.624075           0.624167        0.000091         0.000346     -0.000032
   STARE    im0081       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0081_comparison.png           0.605255           0.605346        0.000091         0.000203      0.000000
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\35_comparison.png           0.311197           0.311286        0.000090         0.001429      0.000000
   STARE    im0139       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0139_comparison.png           0.562790           0.562874        0.000083         0.000321     -0.000029
CHASEDB1 Image_10R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_10R_comparison.png           0.381008           0.381086        0.000078         0.000469      0.000000
```

## Worst F1 Drops

```text
dataset image_id                                                                                                                 comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
  DRIVE       31     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\31_comparison.png           0.434681           0.433937       -0.000744        -0.000530     -0.000754
  DRIVE       37     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\37_comparison.png           0.400560           0.399900       -0.000660        -0.000303     -0.000589
  DRIVE       39     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\39_comparison.png           0.580494           0.579840       -0.000655         0.000331     -0.000952
  DRIVE       36     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\36_comparison.png           0.524452           0.523815       -0.000637         0.000069     -0.000669
  DRIVE       33     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\33_comparison.png           0.575911           0.575338       -0.000572         0.000300     -0.000750
  DRIVE       21     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\21_comparison.png           0.589952           0.589470       -0.000481        -0.000067     -0.000568
  DRIVE       30     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\30_comparison.png           0.443922           0.443492       -0.000430        -0.000214     -0.000386
  STARE   im0005 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0005_comparison.png           0.464894           0.464584       -0.000310         0.000111     -0.000444
  DRIVE       26     E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\26_comparison.png           0.536128           0.535846       -0.000281        -0.000120     -0.000291
  STARE   im0082 E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0082_comparison.png           0.496369           0.496103       -0.000265         0.001834     -0.000510
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                       comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0002       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0002_comparison.png           0.084493           0.084493        0.000000         0.000000           0.0
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_13R_comparison.png           0.105578           0.105578        0.000000         0.000000           0.0
   STARE    im0235       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0235_comparison.png           0.182542           0.182542        0.000000         0.000000           0.0
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_01R_comparison.png           0.243598           0.243598        0.000000         0.000000           0.0
CHASEDB1 Image_12R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_12R_comparison.png           0.245927           0.245927        0.000000         0.000000           0.0
   DRIVE        38           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\38_comparison.png           0.284718           0.284718        0.000000         0.000000           0.0
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_05R_comparison.png           0.291760           0.291760        0.000000         0.000000           0.0
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\23_comparison.png           0.294977           0.295078        0.000102         0.000284           0.0
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_04L_comparison.png           0.295148           0.295148        0.000000         0.000000           0.0
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_02R_comparison.png           0.302938           0.302938        0.000000         0.000000           0.0
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                                       comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   STARE    im0082       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0082_comparison.png            0.907279            0.909113         0.001834     -0.000510       -0.000265
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\35_comparison.png            0.878675            0.880104         0.001429      0.000000        0.000090
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0001_comparison.png            0.544856            0.545666         0.000810      0.000000        0.000245
CHASEDB1 Image_06L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_06L_comparison.png            0.781966            0.782655         0.000689      0.000000        0.000134
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_07R_comparison.png            0.728729            0.729368         0.000639      0.000000        0.000095
   STARE    im0255       E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\STARE\comparison\im0255_comparison.png            0.843595            0.844212         0.000617     -0.000264       -0.000090
   DRIVE        28           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\28_comparison.png            0.795767            0.796309         0.000542      0.000000        0.000092
CHASEDB1 Image_10R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_10R_comparison.png            0.661517            0.661985         0.000469      0.000000        0.000078
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_03L_comparison.png            0.790811            0.791216         0.000406      0.000000        0.000064
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_06R_comparison.png            0.731972            0.732353         0.000381      0.000000        0.000057
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                       comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        31           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\31_comparison.png            0.587867            0.587337        -0.000530     -0.000754       -0.000744
   DRIVE        37           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\37_comparison.png            0.717033            0.716731        -0.000303     -0.000589       -0.000660
   DRIVE        30           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\30_comparison.png            0.779817            0.779603        -0.000214     -0.000386       -0.000430
   DRIVE        26           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\26_comparison.png            0.788519            0.788399        -0.000120     -0.000291       -0.000281
   DRIVE        21           E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\DRIVE\comparison\21_comparison.png            0.816467            0.816400        -0.000067     -0.000568       -0.000481
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_01L_comparison.png            0.699661            0.699661         0.000000      0.000000        0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_02R_comparison.png            0.623959            0.623959         0.000000      0.000000        0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_01R_comparison.png            0.577452            0.577452         0.000000      0.000000        0.000000
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_08R_comparison.png            0.658154            0.658154         0.000000      0.000000        0.000000
CHASEDB1 Image_07L E:\ca_apsrg_retinal_project\outputs\method_ablation\experiments_a04_selective_hybrid_bfs\CHASEDB1\comparison\Image_07L_comparison.png            0.736494            0.736494         0.000000      0.000000        0.000000
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\method_ablation\analysis_a04_selective_hybrid_bfs\plots\delta_iou_by_dataset.png`
