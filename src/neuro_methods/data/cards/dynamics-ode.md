# 动力系统与观测模型

ID：`dynamics-ode` · 领域：dynamics · 实现：reference_only

## 研究问题

让潜在状态、模型参数和实际测量之间的关系可检验。

## 流程、输入输出与检查

执行路径：记录方程、单位、初值、参数和观测映射；先验证简化模型；改变积分容差或步长检查稳定性；再增加节点、耦合、噪声和 BOLD 等观测环节。

质量与解释边界：数值不稳定不等于真实动力学转变；潜在神经变量不是 BOLD。尚未在本库包装求解器或全脑平台。

当前仅完成方法卡，尚未包装运行流程。下一步必须由具体研究数据和问题确定最小可验收案例。

## 来源

- [一手来源](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)；核查：2026-09-08
- [一手来源](https://github.com/the-virtual-brain/tvb-root)；核查：2026-09-08

## 验证与使用记录

初始状态：source_reviewed_not_run。本地测试证据见 docs/VALIDATION.md。所有真实项目的科学验收目前均未完成。

新增项目记录应包含：研究问题、数据范围、库版本、配置、质控、敏感性检查、失败条件、研究者结论。
