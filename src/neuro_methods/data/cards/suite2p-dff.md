# Suite2p 数值结果导入与 ΔF/F

ID：`suite2p-dff` · 领域：calcium · 实现：implemented

## 研究问题

导入 F、Fneu、iscell，保留原 ROI 编号，显式神经毡校正后计算本库定义的 ΔF/F。

## 流程、输入输出与检查

输入：F.npy 与 Fneu.npy (roi,time)，iscell.npy (roi,2)；其中第一列为 0/1 标签，第二列为分类概率。保留原行号 roi_ids，避免丢失筛选前后对应关系。

流程：核对尺寸 → 按明确的 cells_only 选择 → Fcorrected=F-alpha*Fneu → 全局百分位 ΔF/F → 保存原始、背景及校正后信号。

必须明确提供 neuropil_coefficient、cells_only、sampling_rate_hz 和 upstream.suite2p_version（无法获得时明确写 unknown，不能猜）。示例配置里的数值只用于演示。

不加载需要 pickle 的 stat.npy/settings.npy/ops.npy；不执行 Suite2p 提取、不把 spks 与 F 混合。这是数值结果适配器，尚无真实 Suite2p 数据验证。

调用：`neuro-methods run configs/suite2p-dff.json --output runs/s2p-001`。

验收：用已知夹具验证校正、筛选及 ROI 编号；在目标数据检查 alpha、基线及 iscell 筛选的敏感性。

## 来源

- [一手来源](https://github.com/MouseLand/suite2p)；核查：2026-09-08

## 验证与使用记录

初始状态：fixture_verified。本地测试证据见 docs/VALIDATION.md。所有真实项目的科学验收目前均未完成。

新增项目记录应包含：研究问题、数据范围、库版本、配置、质控、敏感性检查、失败条件、研究者结论。
