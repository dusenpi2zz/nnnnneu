# 描述性 Pearson 相关矩阵

ID：`pearson` · 领域：networks · 实现：implemented

## 研究问题

明确 roi × time 的输入，产生描述性相关矩阵并拒绝常数序列。

## 流程、输入输出与检查

输入：完成必要前处理的有限实数矩阵 (roi,time)，至少两条非常数序列、三个采样点。记录实际采样率。

计算：Pearson 相关矩阵；输出 correlation。软件不执行滤波、去混杂、显著性检验、阈值化或因果分析。

检查：对称性、对角线、已知正负相关、常数及缺失值；解释前评估自相关、共同驱动、运动及预处理影响。

调用：`neuro-methods run configs/pearson.json --output runs/corr-001`。

边界：相关矩阵是描述量，不能直接解释为结构连接、有效连接或机制；增加时间点也不消除混杂。

## 来源

- [一手来源](https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html)；核查：2026-09-08

## 验证与使用记录

初始状态：analytic_verified。本地测试证据见 docs/VALIDATION.md。所有真实项目的科学验收目前均未完成。

新增项目记录应包含：研究问题、数据范围、库版本、配置、质控、敏感性检查、失败条件、研究者结论。
