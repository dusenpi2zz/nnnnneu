# 钙成像工具整合

原图是一份历史工具表，混合了算法、工具箱、GUI 和流程；文章年份不等于软件当前版本。

## 按任务选择入口

| 实际任务 | 起始入口 | 前置判断 |
|---|---|---|
| 双光子视频的自动细胞提取 | Suite2p 或 Python CaImAn | 细胞/树突对象、采样率、运动和背景 |
| 单光子 miniscope 数据 | CaImAn CNMF-E；需要复现时查 MIN1PIPE/CNMF-E MATLAB | 单光子背景、DAQ 版本和尺度 |
| 已有可靠 ROI，只需提取和归一化 | 本库 roi-dff | 先校正运动；ROI 无重叠；基线适用 |
| 已有 Suite2p 输出，希望复用后处理 | 本库 suite2p-dff | 同一 plane/session；alpha 与 iscell 已审查 |
| 跨天追踪细胞 | CellReg | 各 session 已得到空间足迹并统一坐标 |
| 重现旧论文 | 原论文指定工具与提交 | 保留历史环境，不盲目升级 |

这是第一版的选择建议，不是性能排名。未在同一目标数据集开展基准比较。

## 概念与依赖

- CNMF/CNMF-E 是方法；CaImAn 是实现方法的工具箱。
- MiniscopeAnalysis 已组合 NoRMCorre 与 CNMF-E；EZcalcium 也调用已有工具。
- NoRMCorre 做运动校正；CellReg 做跨 session 细胞匹配；两种“配准”不在同一层。
- 图中的两个 CellReg 链接分别收录，不计为两个独立算法。
- CaImAn-MATLAB 和 MiniscopeAnalysis README 明确不再维护。其他条目的维护活跃度未全面审计。
- MOSAIC 原始链接本次未能打开；具体插件未确定，保留为待核实项。

## 现成平台如何复用

[OptiNiSt](https://github.com/oist/optinist) 已组合多种分析工具与工作流；[mesmerize-core](https://mesmerize-core.readthedocs.io/en/latest/) 支持 CaImAn 运行及参数组织；[NeuroConv](https://neuroconv.readthedocs.io/en/main/how_to/annotate_ophys_metadata.html) 提供成像分析结果到 NWB 的转换接口。后续优先复用这些项目完成合适的环节，个人库专注方法选择、固定配置、验证和经验积累。

## 比较工具时必须保留的变量

同一输入片段、成像方式、帧率、空间尺度、细胞密度、背景强度、运动、人工真值来源、参数搜索预算和纳入规则。记录时间与内存开销；不能仅凭“提取的细胞更多”认定更好。

有标注时分别检查检出、重复、漏检与信号质量；无真值时只能报告一致性、稳定性和可视化证据，不能声称准确率。合成示例只验证特定生成假设下的软件行为。

全部条目与原始来源见 [目录](CATALOG.md)。核查日期：2026-09-08。
