# 固定 ROI 荧光提取与 ΔF/F

ID：`roi-dff` · 领域：calcium · 实现：implemented

## 研究问题

校正后视频 + 非重叠二值 ROI → 平均荧光和全局百分位基线 ΔF/F。

## 流程、输入输出与检查

输入：数值 `.npy` 视频 (time,row,col)，二值掩模 (roi,row,col)，正采样率。必须显式声明已完成运动校正。

流程：按帧分块 → ROI 像素均值 → 每条轨迹全局 percentile 基线 F0 → (F-F0)/F0 → 数值 QC、图和运行记录。

参数：percentile 默认 20；chunk_frames 默认 128；min_baseline 默认 1e-6。这些是软件默认值，不是普适科学最优值。

拒绝空或重叠 ROI、NaN/Inf、非数值输入、非正基线；不会自动分割、去重叠、校正运动或推断放电。漂白或持续活动时应先评估基线模型。

调用：`neuro-methods run configs/roi-dff.json --output runs/roi-001`。先把配置中路径和采样率改为真实值。合成示例无需外部文件：`neuro-methods demo --output runs/demo-001`。

验收：解析例子的 ROI 均值和 ΔF/F 正确；含噪合成荧光 RMSE < 0.15；真实视频还需人工 ROI/配准 QC 和基线敏感性。

## 来源

本库原创工作流定义，详细公式见 signals.py；演示验证属于软件验证。

## 验证与使用记录

初始状态：synthetic_verified。本地测试证据见 docs/VALIDATION.md。所有真实项目的科学验收目前均未完成。

新增项目记录应包含：研究问题、数据范围、库版本、配置、质控、敏感性检查、失败条件、研究者结论。
