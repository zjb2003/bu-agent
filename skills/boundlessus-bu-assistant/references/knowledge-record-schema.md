# 知识库记录最小协议

这份协议用于把原始资料转成可检索、可审核、可追溯的记录。它是运行时边界，不要求普通用户看到全部元数据。

## 必填字段

```yaml
id: stable-record-id
title: 简短标题
content: 可核验正文
type: project_profile | resource | course | activity | writing_template | safety_rule | cooperation
status: confirmed | approved | draft | internal | expired | unknown
sensitivity: public | internal | child_data | restricted | unknown
source: 来源文件、负责人或可核验链接
updated_at: YYYY-MM-DD
owner: 维护责任人或角色
next_review: YYYY-MM-DD
allowed_use: answer | internal_only | no_externalization
```

## 状态判定

- `confirmed`：资料中明确出现，且没有已知冲突；可以作为项目事实使用。
- `approved`：已完成项目方审核，且允许在对应范围内对外使用。
- `draft`：正在编辑或尚未审核；只能作为内部草稿，不能包装成正式事实。
- `internal`：仅供内部工作；不得对外复述或转发。
- `expired`：已过复核日期或明确被替代；不得回答为当前有效。
- `unknown`：无法判断来源、时间、授权或状态；按待确认处理。

## 处理规则

1. `sensitivity=child_data` 或 `restricted` 时，检索结果默认脱敏；没有必要性和授权，不把原文带入回答。
2. 真实姓名、学校、电话、社交账号、照片、书信原文和可组合识别信息不放入标题、标签或摘要。
3. 同一事实存在多个版本时保留 `conflict_group`，分别记录来源和日期，不通过“内容更完整”自行选定版本。
4. 没有 `source`、`updated_at` 或 `owner` 的记录不得进入“正式对外事实”集合。
5. `allowed_use=internal_only` 或 `no_externalization` 时，即使检索命中，也只能说明存在内部资料，不能输出其内容。

## 对外前检查

对外事实至少同时满足：`status=confirmed` 或 `approved`、`sensitivity=public`、有来源、有更新时间、未过期、允许对外使用。其余记录只能支持“待确认”“内部草稿”或“当前资料中未找到”的边界性表述。
