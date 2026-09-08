# 持续扩充方法库

## 增加一条方法

1. 先检索：`neuro-methods search 关键词`，避免重复条目。
2. 建草稿：`neuro-methods new-method method-id --output drafts`。
3. 填写研究问题、适用/不适用条件、输入输出、假设、操作步骤、参数、QC、失败例和一手来源。
4. 将完整卡片移到 `src/neuro_methods/data/cards/`；向 `catalog.json` 添加唯一 ID、domain、kind、implementation、validation、upstream_status、summary、tags、sources、card。
5. 执行测试，检查 CLI 中可以 search/show；更新 docs/CATALOG.md。

卡片和目录都是 UTF-8 文件，直接编辑即可。catalog 是安装包内离线索引；editable 安装会反映源文件修改，wheel 安装需重新构建安装。

## 验证状态

| 状态 | 最低证据 |
|---|---|
| source_reviewed_not_run | 一手来源、核查日期、适用范围；不承诺能执行 |
| synthetic_verified | 可复现生成数据、已知预期、数值测试和失败测试 |
| fixture_verified | 已知输入输出的格式/接口夹具；不是上游端到端验证 |
| analytic_verified | 对照可手算或解析结果 |
| replay_verified | 输入、配置、源码和版本漂移会被拒绝；已完成重放测试 |
| project_verified | 特定真实项目的质量、敏感性和解释边界由研究者验收 |

维护状态单独记录。工具活跃不代表适合研究；旧工具可能仍适合精确复现。新版本、平台或数据变化后，原验证范围不能自动外推。

## 增加运行流程

先写明确输入/输出与失败条件，优先薄适配器；使用独立环境和固定版本；外部后端应保存自身配置与引用。增加正例、科学相关负例和最小运行证据后再标记 implemented。

不要复制论文全文、付费附件、上游完整源码或未授权数据。代码复用前检查具体许可；本库 MIT 不能替代上游授权。

## 项目使用记录模板

复制 `templates/project-use.md`，写明问题、方法 ID、数据范围、代码版本、配置、结果证据、失败与研究者判断。受限数据的记录保存在获准环境，公共/共享条目只留下允许披露的经验。

## 版本策略

修改算法定义、默认值或输出语义时更新版本与 CHANGELOG；不要修改旧运行结果“适配新代码”。从真实项目发现重复需求后，再把稳定部分归入通用库。
