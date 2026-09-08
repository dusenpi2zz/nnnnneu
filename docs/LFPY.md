# LFPy 模块

本模块连接“细胞形态和跨膜电流”与“电极测量”，适合积累观测模型的假设、模拟和验证经验。参见 [工具卡](../src/neuro_methods/data/cards/lfpy.md) 与 [运行卡](../src/neuro_methods/data/cards/lfpy-passive-demo.md)。

## 独立安装

首个 CI 目标为 Ubuntu 24.04、Python 3.10；固定依赖见 environments/lfpy-linux.txt。LFPy 2.3.7 的已发布 Linux wheel 对应 CPython 3.10 和 manylinux_2_39；其他平台可能需要编译或使用不同受支持安装路径。当前 Windows 机器未配置 WSL，也没有 LFPy/NEURON，基础方法库可照常运行。

以下在上述 Linux 环境、仓库目录执行：

```bash
python3.10 -m venv .venv-lfpy
.venv-lfpy/bin/python -m pip install -r environments/lfpy-linux.txt
.venv-lfpy/bin/python -m pip install . --no-deps
.venv-lfpy/bin/neuro-methods lfpy-demo --output runs/lfpy-001
.venv-lfpy/bin/neuro-methods replay runs/lfpy-001/manifest.json --output runs/lfpy-replay
```

Python 调用：

```python
from neuro_methods.lfpy_demo import run_lfpy_demo
run_lfpy_demo("runs/lfpy-001", dt_ms=0.0625, sigma=0.3)
```

`pip install .[lfpy,plot]` 是另一种安装可选依赖的方式，仍须在兼容平台上使用。安装基础包不会自动拉入 NEURON 或 LFPy。

## 首个例子的实际范围

使用内置原创形态和被动膜，保存单位与全部协议。采用 LFPy 的 Cell、Synapse、LineSourcePotential 接口，记录跨膜电流和三个位置的电位；通过电导率缩放检查确认正向映射的基本行为。完整输出与边界在运行卡中列明。

## 验证状态

本地 Windows 仅验证包结构、参数拒绝和缺依赖提示；LFPy 模拟测试在未安装依赖时明确跳过。2026-09-09 的 [Linux CI](https://github.com/dusenpi2zz/nnnnneu/actions/runs/34248514292) 已实际安装后端并完成仿真、数值检查和重放，2 个测试通过、无跳过。验证参数与边界见 [验证记录](VALIDATION.md)。

后续真实研究需追加：形态与机制来源、采样和空间离散收敛、电极几何/电导率敏感性、介质边界，以及与真实数据对照的可辨识性分析。原始 LFP/EEG 记录的清洗与统计分析是另一个流程。

官方安装与发布入口：[LFPy](https://github.com/LFPy/LFPy)、[LFPy PyPI](https://pypi.org/project/LFPy/)、[NEURON PyPI](https://pypi.org/project/neuron/)。核查日期：2026-09-08。
