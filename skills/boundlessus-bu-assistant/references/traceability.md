# 原始材料到 Skill 结构的映射

本 Skill 包由 `BU小助手预设` 中的原始材料整理而来。原始文件在父目录保留不变；以下是运行时的单一入口和按需参考层。

| 原始材料 | 新结构中的用途 |
|---|---|
| `BU小助手基本设定.md` | `project-profile.md`、`audience-and-task-routing.md` |
| `BU小助手系统提示词-mixed.md` | 由根目录 `SKILL.md` 的运行顺序、固定边界和完成检查替代；原文件保留作对照 |
| `BU小助手用户识别与分层回应规则.md` | `audience-and-task-routing.md` |
| `BU小助手知识库调用规则与资料边界.md` | `knowledge-and-boundaries.md` |
| `BU小助手分角色任务处理流程与回答结构.md` | `audience-and-task-routing.md`、`output-contracts.md` |
| `BU小助手回答风格免责声明儿童保护与隐私数据安全规范.md` | `safety-and-referral.md`、`output-contracts.md` |
| `BU小助手拒答转介与风险处置规则.md` | `safety-and-referral.md` |
| `BU小助手常见场景标准回答与示例问答.md` | `references/scenario-examples-source.md`，仅按需读取 |
| `BoundlessUs知识库建设与资料上传规范.md` | `knowledge-governance.md` 与 `references/knowledge-governance-source.md` |
| `BU小助手上线前测试问题清单.md` | `evals/launch-tests-source.md`，仅用于发布前回归 |

运行时优先执行 `SKILL.md` 的顺序与安全门；详细原始材料不能覆盖安全、事实和授权边界。`runtime-contract.md` 规定宿主输入与能力边界，`knowledge-record-schema.md` 规定知识记录状态，`deployment-checklist.md` 规定接入、切换和回滚，`qingxiaoda-adapter.md` 规定清小搭映射与平台待核实项，`evals/cases.jsonl`、`evals/grading-rubric.md` 与 `evals/host-run-template.md` 规定可重复的发布前回归。
