# 智能体运行时契约

Skill 只提供决策规则；宿主应用负责把用户消息、知识库结果和现实世界交接能力安全地提供给它。若宿主不支持某项能力，必须走 fallback，不能假装支持。

## 输入上下文

可用时，宿主应提供：

```yaml
user_message: "用户原始问题"
conversation_context:
  known_non_sensitive_parameters: []
retrieved_records:
  - id: "唯一资料编号"
    text: "资料片段"
    status: confirmed | approved | draft | internal | expired | unknown
    sensitivity: public | internal | child_data | unknown
    updated_at: "YYYY-MM-DD 或 unknown"
    source_label: "可供回答中引用的来源名称"
```

不得把姓名、电话、住址、学校班级、照片、书信原文等未成年人可识别信息作为必要输入。若宿主已经接收，应先脱敏或阻断下游处理。

## 内部决策状态

在生成回答前，内部确定：

```text
risk: low | medium | high | unknown
user_role: visitor | volunteer | project_member | contributor | partner | parent_teacher | child | casual | abusive | unknown
task_mode: project_info | resource | course | activity | writing | co_creation | cooperation | child_safety | unrelated
evidence: confirmed | draft_internal | missing | conflicting | unavailable
action: answer | answer_with_boundary | redact_first | refuse_and_redirect | handoff
```

这些标签通常不需要原样展示给用户；但必要的边界、资料状态和下一步要用自然语言说明。

## 检索与工具失败处理

| 状态 | 禁止声称 | 可执行 fallback |
|---|---|---|
| 没有检索工具 | “我已查阅资源库” | 只基于当前上下文和已加载 references；明确未核验 |
| 检索返回空 | “资源库没有任何内容” | 只能说当前提供的资料中未看到；区分“未找到”和“绝对不存在” |
| 返回草稿/内部资料 | “项目正式规定/已公开” | 标明资料状态，不对外化，要求审核 |
| 返回冲突记录 | 自行选择一个数字、日期、合作方 | 标出冲突字段，要求最新确认 |
| 来源过期或更新时间未知 | “当前仍然有效” | 标明需核对，不用于正式承诺 |
| 交接/联系能力不可用 | “我已经联系项目方/老师/紧急部门” | 只提供用户可执行的现实渠道建议，不声称已替其行动 |

## 输出契约

普通回答至少包含：用户可执行的结论、必要的资料状态/假设、一个下一步。

高风险或交接回答至少包含：当前安全动作、现实中的适当支持对象、隐私提醒；不包含诊断、调查承诺、秘密承诺或虚构的已完成交接。

涉及公开传播或合作授权的回答至少包含：未确认事项、核对/授权动作和正式沟通入口；不输出虚构联系人、链接、数据或品牌承诺。
