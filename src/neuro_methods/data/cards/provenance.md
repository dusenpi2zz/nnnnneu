# 可复现运行与研究记录

ID：`provenance` · 领域：reproducibility · 实现：implemented

## 研究问题

保留足以重放和解释一次分析的输入、配置、版本与证据。

## 流程、输入输出与检查

执行路径：记录输入哈希、代码版本、环境、随机种子、配置和输出；保留失败日志；每次运行使用新目录；项目引用固定库版本。

质量与解释边界：重放相同输入与版本不自动保证跨硬件逐位一致；哈希不能证明数据授权或科学正确。软件完成状态与研究者验收状态分开。

当前实现：run 自动生成 manifest、config.resolved、results、summary 和 report；replay 检查哈希及版本。

## 来源

- [一手来源](https://git-scm.com/docs)；核查：2026-09-08
- [一手来源](https://numpy.org/doc/stable/reference/generated/numpy.load.html)；核查：2026-09-08

## 验证与使用记录

初始状态：replay_verified。本地测试证据见 docs/VALIDATION.md。所有真实项目的科学验收目前均未完成。

新增项目记录应包含：研究问题、数据范围、库版本、配置、质控、敏感性检查、失败条件、研究者结论。
