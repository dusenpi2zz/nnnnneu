# 方法目录

研究问题优先；工具引用、运行接口、科学验证分开记录。

| 方法/工具 | 领域 | 本库实现 | 上游状态 |
|---|---|---|---|
| [ROI analysis / MOSAIC ImageJ](../src/neuro_methods/data/cards/mosaic-roi.md) | calcium | reference_only | unresolved |
| [CellSort / PCA-ICA](../src/neuro_methods/data/cards/cellsort.md) | calcium | reference_only | not_assessed |
| [SIMA](../src/neuro_methods/data/cards/sima.md) | calcium | reference_only | not_assessed |
| [SamuROI](../src/neuro_methods/data/cards/samuroi.md) | calcium | reference_only | not_assessed |
| [CaImAn-MATLAB / CNMF](../src/neuro_methods/data/cards/caiman-matlab.md) | calcium | reference_only | explicitly_unmaintained |
| [CNMF-E (MATLAB)](../src/neuro_methods/data/cards/cnmfe-matlab.md) | calcium | reference_only | not_assessed |
| [MiniscopeAnalysis](../src/neuro_methods/data/cards/miniscope-analysis.md) | calcium | reference_only | explicitly_unmaintained |
| [MIN1PIPE](../src/neuro_methods/data/cards/min1pipe.md) | calcium | reference_only | not_assessed |
| [Suite2p](../src/neuro_methods/data/cards/suite2p.md) | calcium | reference_only | not_assessed |
| [EZcalcium](../src/neuro_methods/data/cards/ezcalcium.md) | calcium | reference_only | not_assessed |
| [TENASPIS](../src/neuro_methods/data/cards/tenaspis.md) | calcium | reference_only | not_assessed |
| [CellReg (Ziv lab)](../src/neuro_methods/data/cards/cellreg.md) | calcium | reference_only | not_assessed |
| [CellReg (JinghaoLu 链接)](../src/neuro_methods/data/cards/cellreg-jinghao.md) | calcium | reference_only | fork_verified_support_not_assessed |
| [CaImAn (Python)](../src/neuro_methods/data/cards/caiman-python.md) | calcium | reference_only | not_assessed |
| [NoRMCorre](../src/neuro_methods/data/cards/normcorre.md) | calcium | reference_only | not_assessed |
| [固定 ROI 荧光提取与 ΔF/F](../src/neuro_methods/data/cards/roi-dff.md) | calcium | implemented | not_applicable |
| [Suite2p 数值结果导入与 ΔF/F](../src/neuro_methods/data/cards/suite2p-dff.md) | calcium | implemented | not_applicable |
| [描述性 Pearson 相关矩阵](../src/neuro_methods/data/cards/pearson.md) | networks | implemented | not_applicable |
| [fMRI 前处理与质控](../src/neuro_methods/data/cards/fmri-qc.md) | fmri | reference_only | not_applicable |
| [时间序列特征与预测验证](../src/neuro_methods/data/cards/timeseries-features.md) | timeseries | reference_only | not_applicable |
| [网络指标与匹配零模型](../src/neuro_methods/data/cards/network-nulls.md) | networks | reference_only | not_applicable |
| [动力系统与观测模型](../src/neuro_methods/data/cards/dynamics-ode.md) | dynamics | reference_only | not_applicable |
| [参数恢复与实际可辨识性](../src/neuro_methods/data/cards/identifiability.md) | identifiability | reference_only | not_applicable |
| [可复现运行与研究记录](../src/neuro_methods/data/cards/provenance.md) | reproducibility | implemented | not_applicable |

| [LFPy 细胞外电位正向建模](../src/neuro_methods/data/cards/lfpy.md) | electrophysiology | reference_only | not_assessed |
| [LFPy 被动细胞最小正向模型](../src/neuro_methods/data/cards/lfpy-passive-demo.md) | electrophysiology | implemented | not_assessed |

`reference_only` 不提供后端执行；`not_assessed` 不等于已停止维护。图中的两个 CellReg 链接分别保留，但不计作两个独立算法。
