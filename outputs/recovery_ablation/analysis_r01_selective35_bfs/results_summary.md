# CA-APSRG Experiment Summary

Source results file: `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\metrics_per_image.csv`

## Article-style Summary Table

```text
 dataset         method  n_images       precision          recall        f1_score             iou        accuracy
CHASEDB1 APSRG Baseline        28 0.6924 ± 0.0980 0.3578 ± 0.1234 0.4552 ± 0.0955 0.2994 ± 0.0803 0.9434 ± 0.0084
CHASEDB1       CA-APSRG        28 0.6925 ± 0.0981 0.3578 ± 0.1234 0.4552 ± 0.0955 0.2994 ± 0.0803 0.9434 ± 0.0084
   DRIVE APSRG Baseline        20 0.7795 ± 0.1131 0.3726 ± 0.0897 0.4979 ± 0.0942 0.3363 ± 0.0809 0.9080 ± 0.0158
   DRIVE       CA-APSRG        20 0.7796 ± 0.1131 0.3723 ± 0.0896 0.4977 ± 0.0942 0.3361 ± 0.0809 0.9080 ± 0.0158
   STARE APSRG Baseline        20 0.7075 ± 0.1253 0.4401 ± 0.1332 0.5255 ± 0.1014 0.3621 ± 0.0879 0.9425 ± 0.0108
   STARE       CA-APSRG        20 0.7076 ± 0.1253 0.4400 ± 0.1332 0.5255 ± 0.1014 0.3621 ± 0.0879 0.9425 ± 0.0108
```

## Mean Improvement by Dataset

```text
 dataset  n_images  delta_precision_mean  delta_recall_mean  delta_f1_score_mean  delta_iou_mean  f1_score_n_improved  f1_score_n_equal  f1_score_n_decreased
CHASEDB1        28              0.000068          -0.000012        -3.295134e-07   -9.067444e-07                    5                21                     2
   DRIVE        20              0.000123          -0.000294        -2.432679e-04   -2.205949e-04                    3                 7                    10
   STARE        20              0.000090          -0.000055        -1.621597e-05   -1.655390e-05                    1                15                     4
```

## Full Summary by Dataset and Method

```text
 dataset         method  n_images  precision_mean  precision_std  recall_mean  recall_std  f1_score_mean  f1_score_std  iou_mean  iou_std  accuracy_mean  accuracy_std
CHASEDB1 APSRG Baseline        28        0.692410       0.098038     0.357845    0.123420       0.455151      0.095460  0.299399 0.080290       0.943412      0.008382
CHASEDB1       CA-APSRG        28        0.692478       0.098069     0.357833    0.123422       0.455150      0.095454  0.299398 0.080285       0.943414      0.008380
   DRIVE APSRG Baseline        20        0.779517       0.113096     0.372561    0.089664       0.497898      0.094228  0.336281 0.080937       0.907975      0.015832
   DRIVE       CA-APSRG        20        0.779641       0.113078     0.372267    0.089618       0.497655      0.094193  0.336060 0.080896       0.907959      0.015823
   STARE APSRG Baseline        20        0.707469       0.125295     0.440058    0.133167       0.525537      0.101428  0.362149 0.087917       0.942497      0.010845
   STARE       CA-APSRG        20        0.707558       0.125272     0.440003    0.133165       0.525521      0.101415  0.362133 0.087904       0.942501      0.010839
```

## Best F1 Improvements

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\STARE\comparison\im0001_comparison.png           0.424373           0.424618        0.000245         0.000810      0.000000
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\23_comparison.png           0.294977           0.295078        0.000102         0.000284      0.000000
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_07R_comparison.png           0.397964           0.398059        0.000095         0.000639      0.000000
   DRIVE        25           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\25_comparison.png           0.624075           0.624167        0.000091         0.000346     -0.000032
CHASEDB1 Image_13L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_13L_comparison.png           0.459228           0.459299        0.000071         0.000236      0.000000
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_03L_comparison.png           0.442942           0.443006        0.000064         0.000406      0.000000
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_06R_comparison.png           0.398999           0.399055        0.000057         0.000381      0.000000
CHASEDB1 Image_01R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_01R_comparison.png           0.423579           0.423613        0.000034         0.000251      0.000000
   DRIVE        27           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\27_comparison.png           0.512856           0.512859        0.000002         0.000307     -0.000069
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_02R_comparison.png           0.302938           0.302938        0.000000         0.000000      0.000000
```

## Worst F1 Drops

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\35_comparison.png           0.504271           0.502947       -0.001324         0.000488     -0.001363
   DRIVE        22           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\22_comparison.png           0.483983           0.483306       -0.000676        -0.000123     -0.000671
   DRIVE        37           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\37_comparison.png           0.400560           0.399900       -0.000660        -0.000303     -0.000589
   DRIVE        39           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\39_comparison.png           0.580494           0.579840       -0.000655         0.000331     -0.000952
   DRIVE        33           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\33_comparison.png           0.575911           0.575338       -0.000572         0.000300     -0.000750
   DRIVE        21           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\21_comparison.png           0.589952           0.589470       -0.000481        -0.000067     -0.000568
   STARE    im0005       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\STARE\comparison\im0005_comparison.png           0.464894           0.464584       -0.000310         0.000111     -0.000444
   DRIVE        38           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\38_comparison.png           0.583330           0.583080       -0.000250         0.000114     -0.000351
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\34_comparison.png           0.318816           0.318581       -0.000235         0.000060     -0.000186
CHASEDB1 Image_03R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_03R_comparison.png           0.456830           0.456600       -0.000230         0.000037     -0.000235
```

## Worst Ca F1 Cases

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_f1_score  ca_apsrg_f1_score  delta_f1_score  delta_precision  delta_recall
   STARE    im0139       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\STARE\comparison\im0139_comparison.png           0.232102           0.232102        0.000000         0.000000      0.000000
CHASEDB1 Image_13R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_13R_comparison.png           0.265540           0.265540        0.000000         0.000000      0.000000
   DRIVE        23           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\23_comparison.png           0.294977           0.295078        0.000102         0.000284      0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_02R_comparison.png           0.302938           0.302938        0.000000         0.000000      0.000000
   DRIVE        34           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\34_comparison.png           0.318816           0.318581       -0.000235         0.000060     -0.000186
CHASEDB1 Image_02L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_02L_comparison.png           0.334125           0.334125        0.000000         0.000000      0.000000
CHASEDB1 Image_04R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_04R_comparison.png           0.341741           0.341741        0.000000         0.000000      0.000000
CHASEDB1 Image_10R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_10R_comparison.png           0.343175           0.343175        0.000000         0.000000      0.000000
CHASEDB1 Image_12L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_12L_comparison.png           0.355069           0.355069        0.000000         0.000000      0.000000
   DRIVE        31           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\31_comparison.png           0.366738           0.366738        0.000000         0.000000      0.000000
```

## Best Precision Improvements

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   STARE    im0001       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\STARE\comparison\im0001_comparison.png            0.544856            0.545666         0.000810      0.000000        0.000245
CHASEDB1 Image_07R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_07R_comparison.png            0.728729            0.729368         0.000639      0.000000        0.000095
   STARE    im0255       E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\STARE\comparison\im0255_comparison.png            0.843595            0.844212         0.000617     -0.000264       -0.000090
   DRIVE        32           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\32_comparison.png            0.764576            0.765101         0.000525     -0.000148       -0.000055
   DRIVE        35           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\35_comparison.png            0.889930            0.890418         0.000488     -0.001363       -0.001324
CHASEDB1 Image_03L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_03L_comparison.png            0.790811            0.791216         0.000406      0.000000        0.000064
CHASEDB1 Image_06R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_06R_comparison.png            0.731972            0.732353         0.000381      0.000000        0.000057
   DRIVE        25           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\25_comparison.png            0.769419            0.769765         0.000346     -0.000032        0.000091
   DRIVE        39           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\39_comparison.png            0.775928            0.776259         0.000331     -0.000952       -0.000655
   DRIVE        27           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\27_comparison.png            0.788104            0.788411         0.000307     -0.000069        0.000002
```

## Worst Precision Drops

```text
 dataset  image_id                                                                                                                    comparison_path  baseline_precision  ca_apsrg_precision  delta_precision  delta_recall  delta_f1_score
   DRIVE        37           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\37_comparison.png            0.717033            0.716731        -0.000303     -0.000589       -0.000660
   DRIVE        22           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\22_comparison.png            0.800837            0.800714        -0.000123     -0.000671       -0.000676
   DRIVE        21           E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\DRIVE\comparison\21_comparison.png            0.816467            0.816400        -0.000067     -0.000568       -0.000481
CHASEDB1 Image_05R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_05R_comparison.png            0.823279            0.823240        -0.000038     -0.000098       -0.000100
CHASEDB1 Image_04L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_04L_comparison.png            0.738296            0.738296         0.000000      0.000000        0.000000
CHASEDB1 Image_06L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_06L_comparison.png            0.786293            0.786293         0.000000      0.000000        0.000000
CHASEDB1 Image_02R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_02R_comparison.png            0.623959            0.623959         0.000000      0.000000        0.000000
CHASEDB1 Image_01L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_01L_comparison.png            0.781872            0.781872         0.000000      0.000000        0.000000
CHASEDB1 Image_08R E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_08R_comparison.png            0.780823            0.780823         0.000000      0.000000        0.000000
CHASEDB1 Image_08L E:\ca_apsrg_retinal_project\outputs\recovery_ablation\experiments_r01_selective35_bfs\CHASEDB1\comparison\Image_08L_comparison.png            0.632270            0.632270         0.000000      0.000000        0.000000
```

## Saved Plots

- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\precision_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\recall_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\f1_score_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\iou_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\accuracy_by_dataset_method.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\delta_precision_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\delta_recall_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\delta_f1_score_by_dataset.png`
- `E:\ca_apsrg_retinal_project\outputs\recovery_ablation\analysis_r01_selective35_bfs\plots\delta_iou_by_dataset.png`
