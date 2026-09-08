# LFPy 被动细胞最小正向模型

ID：`lfpy-passive-demo` · 领域：electrophysiology · 实现：可选后端已编写，后端验证状态见 docs/VALIDATION.md。

## 研究问题

在完全已知的简化模型里，确认突触活动可以经跨膜电流和线源模型映射为细胞外电位，并检验单位与介质参数的影响。

## 输入和协议

无外部数据下载。代码生成原创 soma+dendrite HOC 形态；树突 21 段；被动膜参数、突触位置、20/40 ms 激活、三个电极的位置全部写入运行配置。默认 dt=0.0625 ms，sigma=0.3 S/m；这些数值是演示协议，不是已拟合的生物学参数。

## 调用

`neuro-methods lfpy-demo --output runs/lfpy-001`

改变积分步长和电导率：`neuro-methods lfpy-demo --dt-ms 0.03125 --sigma 0.6 --output runs/lfpy-002`。

`neuro-methods replay runs/lfpy-001/manifest.json --output runs/lfpy-replay` 可在相同代码及数值/后端版本下重放。它是专门的示例命令，不使用通用 run 的三种数据输入模板。

## 输出和验收

保存 morphology.hoc、配置、结果、summary、manifest 和研究者报告。结果含 time_ms、soma_mV、synapse_current_nA、membrane_current_nA、extracellular_mV 与 electrode_xyz_um。预览将电极电位转换为 μV。

自动检查有限数值、尺寸、非零响应，以及在相同跨膜电流下将 sigma 加倍使预测电位减半；后者是线性正向模型的实现检查，不是经验发现。记录总跨膜电流残差供审查。后续还需比较更小 dt、更细空间离散化和不同形态的结果。

## 不能推出什么

单个被动细胞示例没有动作电位机制，也没有细胞群、真实 LFP 基准、头模型或参数反演。不能从这个演示推断真实神经活动、EEG/MEG 预测能力已验证，或证明机制可辨识。

## 来源

[LFPy 官方 API 与示例入口](https://github.com/LFPy/LFPy) · 核查：2026-09-08。具体形态、协议、检查和包装代码为本库原创。
