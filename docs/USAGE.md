# 使用说明

## Python API

```python
import numpy as np
from neuro_methods import find_methods, read_card, extract_roi_traces, delta_f_over_f, run_config

print(find_methods("单光子", domain="calcium"))
print(read_card("suite2p-dff"))

# movie: (time, row, col)，masks: (roi, row, col)，均由调用者提供。
# movie = np.load("registered_movie.npy", mmap_mode="r", allow_pickle=False)
# masks = np.load("masks.npy", allow_pickle=False)
# fluorescence = extract_roi_traces(movie, masks)
# dff, baseline = delta_f_over_f(fluorescence, percentile=20)

# 推荐研究运行走配置接口，自动保存证据：
# run_config("configs/roi-dff.json", "runs/project-001")
```

基础数组函数返回数值，不会自动写运行记录；需要留痕时用 run_config 或 CLI。

## 输入约定

- 配置是 UTF-8 JSON，schema_version=1；路径相对**配置文件目录**解析。
- v0.1 只读实数 `.npy`，禁用 pickle；原始 TIFF/HDF5/NWB 需显式转换，不会猜测轴顺序。
- 视频轴为 `(time,row,col)`，ROI 掩模为 `(roi,row,col)`，时间信号为 `(roi,time)`。
- 采样率必须由实际采集信息填写，单位 Hz。不会根据文件名猜测。
- ROI 提取只支持非重叠二值掩模；大量 ROI 时掩模仍驻留内存，不能宣称适合任意规模数据。
- 本库不自动处理去漂白、活动反卷积、时间同步、丢帧或运动校正。

## roi-dff

每个 ROI 每帧取像素均值 F；F0 是整条轨迹的百分位数；输出 `(F-F0)/F0`。静态基线适合作为透明的起始方法，不适用于所有漂白/缓慢漂移数据。任何 F0 小于等于 min_baseline 时停止，避免用截断掩盖问题。

输出：fluorescence、dff 为 ROI×time；baseline 与 roi_ids 为 ROI。ROI 是输入掩模，不是本库检测出的细胞。

## suite2p-dff

在独立 Suite2p 环境完成提取及人工 QC 后，导入同一 plane/session 的 F.npy、Fneu.npy、iscell.npy。iscell 第二列分类概率不用于本库再次阈值化；cells_only=true 使用第一列标签。

输出保留原始 fluorescence、neuropil、corrected_fluorescence、iscell、roi_ids，另算本库定义的 baseline 和 dff。ROI 编号始终对应原输入行号。alpha=0.7 只是模板示例，必须按自己的数据核实，不是自动选择。upstream.suite2p_version 应记录实际版本，缺失时明确 unknown。

不读取 stat.npy/ops.npy/settings.npy，不自动载入 spks.npy，不启动 Suite2p。官方运行入口见 [Suite2p README](https://github.com/MouseLand/suite2p)。

## pearson

只计算描述性相关，要求至少两条非常数轨迹、至少三个采样点。输出 correlation 为 ROI×ROI。没有 p 值、显著性、有效连接或因果估计。输入应由调用者按模态完成必要前处理；fMRI、钙成像和电生理前处理不可互换。

## 重放与迁移

```text
neuro-methods replay runs/demo-001/roi-run/manifest.json --output runs/replay-001
```

重放检查输入及配置哈希、源码指纹和关键数值环境版本；只读原文件，创建新输出。如果把输入移到别的机器，旧绝对路径可能无效：保留旧记录，建立路径更新后的新配置并重新运行，明确记为迁移运行。代码更改后应创建新运行，不修改历史 manifest 来绕过检查。

每次运行的 report.md 留给研究者填写；修改报告后原输出哈希会保留初始版本的证据，后续人工修订应另作 Git/研究记录，不声称与原始哈希一致。重放不依赖人工报告内容。

## 常见失败

| 现象 | 处理 |
|---|---|
| Missing input | 按配置文件所在目录解析路径；先运行 demo 验证安装 |
| masks overlap | 检查 ROI，或改用能进行源分离的上游方法，不偷偷裁掉重叠区域 |
| baseline too small | 检查偏置、背景扣除、漂白及基线模型 |
| No ROIs remain | 核查 iscell 标签；不要仅为得到结果而无条件取消筛选 |
| Input hash changed | 数据变动，另建配置和运行；保留旧记录 |
| no preview | 安装 plot 可选依赖；数值结果不依赖图形组件 |
| Existing output | 使用新的输出目录，不删除或覆盖旧证据 |

## 测试

```text
python -m pytest -q
```

若 Windows 沙箱无法访问系统 pytest 临时目录，指定一个尚不存在的仓库内目录：`python -m pytest -q --basetemp runs/pytest-new`。pytest 会管理 basetemp，切勿指向真实数据或已有结果。
