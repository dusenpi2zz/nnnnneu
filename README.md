# Neuro Methods · 研究方法库

把研究中的方法选择、可运行流程、验证和排错经验积累成可以重复调用的资产。

**v0.2.0 已实现：离线方法检索、固定 ROI 荧光提取与 ΔF/F、Suite2p 数值结果导入、描述性 Pearson 相关、运行留痕和重放；新增可选 LFPy 正向模型示例。**

目前有 26 个方法/工具条目，覆盖钙成像、fMRI、电生理观测模型、时间序列、网络、动力系统、可辨识性和复现。图中全部工具链接已保留；MOSAIC 首行仍待核实具体插件。其他后端作为资料条目，不会自动安装。真实研究数据的科学验收尚未完成。

## 从这里开始

- [按问题查看方法目录](docs/CATALOG.md)
- [钙成像工具整合与选择](docs/CALCIUM.md)
- [LFPy 正向建模与独立环境](docs/LFPY.md)
- [配置、输入输出与 Python 调用](docs/USAGE.md)
- [如何把新方法加入库](CONTRIBUTING.md)
- [验证记录与已知限制](docs/VALIDATION.md)
- [后续扩展顺序](docs/ROADMAP.md)

## 安装

要求 Python 3.10+；首次安装需要访问 Python 包源。下面在仓库目录执行。

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[plot,dev]" -c environments/validated-constraints.txt
.\.venv\Scripts\neuro-methods search 钙成像
.\.venv\Scripts\neuro-methods demo --output runs/demo-001
```

macOS/Linux 使用 `.venv/bin/python` 和 `.venv/bin/neuro-methods`。基础计算只依赖 NumPy；`plot` 增加预览图，`dev` 增加测试依赖。私有 GitHub 仓库需先用自己的已授权 Git 登录克隆，不要把访问令牌写进配置。

激活环境后，可以直接运行：

本机已安装环境时，也可用 `./nm.ps1 search 单光子` 或 `./nm.ps1 show roi-dff`，无需重复安装。

```text
neuro-methods search 单光子
neuro-methods show suite2p-dff
neuro-methods run configs/suite2p-dff.json --output runs/s2p-001
neuro-methods replay runs/demo-001/roi-run/manifest.json --output runs/replay-001
neuro-methods new-method my-method --output drafts
```

`configs/` 是待修改的模板，路径、采样率、神经毡系数均需按数据填写；ROI 模板的 motion_corrected 默认 false，完成实际 QC 后才改为 true。**无需准备数据的命令是 demo**：自动生成合成视频、已知 ROI、提取结果、相关矩阵及预览。

## 一次运行留下什么

| 文件 | 用途 |
|---|---|
| `config.resolved.json` | 含默认参数和解析后输入路径的配置 |
| `manifest.json` | 输入/输出 SHA256、代码指纹、版本、时间与成功/失败状态 |
| `results.npz` | 数值结果；使用 `allow_pickle=False` 读取 |
| `summary.json` | 数组维度、数值 QC 与解释边界 |
| `preview.png` | 安装 plot 后生成的初步检查图 |
| `report.md` | 待研究者完成的质量检查与结论记录 |

旧输出目录不会覆盖。重放要求输入、配置、代码指纹、包版本、Python 和 NumPy 版本匹配；这不是跨硬件逐位一致性的保证。项目应固定库版本，升级后另开一次运行。

## 持续积累

一次新增方法依次经过：**来源已核实 → 示例跑通 → 负例与边界测试 → 项目数据验证**。只收录论文不提升运行状态；通过合成测试也不提升为生物学验证。

方法卡保存在 `src/neuro_methods/data/cards/`，机器可检索目录在 `src/neuro_methods/data/catalog.json`。新方法按研究问题归类，再链接工具。不要将整个第三方仓库复制进来，也不要在一个环境里强装所有后端。

## 数据与发布

库保存代码、配置模板、原创方法摘要和来源链接。实际数据、个体级衍生结果及运行目录默认不纳入 Git；`.gitignore` 不是数据授权机制，运行环境仍须符合数据协议。仓库位于同步目录时，受限数据应在获准环境中另行执行。未经研究者审查的结果不能写成科学发现。

原创代码采用 MIT 许可；上游软件保留各自许可与引用要求，见 [NOTICE](NOTICE.md)。本项目未发布到 PyPI，可从克隆的仓库或本地 wheel 安装。
