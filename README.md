# BoundlessUs BU 小助手 Agent

一个可本地运行、测试和扩展的单 Agent 服务。它先做范围与安全判断，再实际读取
`SKILL.md` 和当前任务所需的 references，最后通过 OpenAI-compatible 模型生成并验证中文回复。

## 安全边界

- 儿童现实危险、侵害、自伤、走失或突发疾病优先进入现实支持/转介路径。
- 手机号、邮箱、身份证样式只记录类型；提示与历史会先脱敏。
- 未授权儿童素材、公开传播与合作授权不会被自动处理、发布或承诺。
- 证据记录仅向模型注入 `public` 且状态允许的内容；冲突资料保持冲突。
- 当前 MVP 不具备真实外部知识库、网页搜索、外部联系、自动提交或发布能力。
- 日志不得加入完整消息、完整提示、密钥或敏感知识原文。若扩展日志，请继续遵守此约束。

## 安装

需要 Python 3.11+：

```bash
cd bu-agent
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env
```

编辑 `.env`，填写服务商提供的 `BASE_URL`、`API_KEY`、`MODEL`。`BASE_URL` 仅规范化末尾
斜杠，不会自动添加 `/v1`；请完全按服务商文档填写。不要提交 `.env`。

## 放置 Skill

本仓库已按交付材料复制到 `skills/boundlessus-bu-assistant/`。也可将该目录挂载到容器并把
`SKILL_PATH` 指向它。启动会检查 `SKILL.md` 及白名单中的必要 references，缺失或路径逃逸会
直接失败。`evals/` 只由评测命令/测试读取，不注入普通对话；旧 mixed 系统提示词不会加载。

```bash
python -m bu_agent.cli check-skill
python -m bu_agent.cli eval --dry-run
```

dry-run 只验证 JSONL 结构，不代表真实模型效果。

## 启动与使用

```bash
uvicorn bu_agent.main:create_app --factory --host 127.0.0.1 --port 8000
python -m bu_agent.cli chat
```

普通请求：

```bash
curl -X POST http://127.0.0.1:8000/v1/chat -H "Content-Type: application/json" -d '{"message":"我第一次去小学支教，怎样准备一节课？","capabilities":{"knowledge_retrieval":false,"web_search":false,"external_contact":false,"publish_or_submit":false}}'
```

SSE 请求：

```bash
curl -N -X POST http://127.0.0.1:8000/v1/chat/stream -H "Content-Type: application/json" -d '{"message":"课堂冷场怎么办？"}'
```

健康检查为 `/health`，就绪检查为 `/ready`，删除会话使用
`DELETE /v1/sessions/{session_id}`。生产默认隐藏调试 metadata；开发时可设置
`EXPOSE_DEBUG_METADATA=true`。

## API 兼容性

默认 `API_MODE=chat_completions`，它通常兼容更多第三方 OpenAI-compatible 服务。
`API_MODE=responses` 使用官方 SDK 的 Responses 接口；若服务商不支持，会返回明确兼容性错误，
应切回 `chat_completions`。适配器只发送保守参数，不依赖 tool calling 或 JSON Schema。

流式端点对低风险普通提问逐段发送模型输出；高风险或隐私相关请求会先完成验证再发送，
因此这类请求首字可能等待更久。部署时反向代理也必须关闭响应缓冲。

## 测试

```bash
pytest
ruff check .
```

测试使用 `FakeLLMProvider`，完全离线，不需要真实密钥，也不会访问外部 API。真实模型效果、
供应商兼容性和线上安全效果不属于离线测试结果。生产部署前必须运行 Skill 自带案例，并完成
人工儿童安全、隐私、事实与授权验收。

## 扩展点

- 新知识源：实现 `KnowledgeProvider.search()`，返回 `EvidenceResult`，并在应用装配时注入；不要
  将 `internal`、`child_data` 或未知敏感度内容直接注入。
- 新会话存储：实现 `ConversationStore` 的 `get/append/delete`。不得建立儿童长期画像；保留 TTL、
  最大轮次和真正删除语义。
- 新模型服务：实现 `LLMProvider.complete/stream`，内部继续使用统一的 `LLMRequest/LLMEvent`。

最短部署步骤：复制 `.env.example` 为 `.env`，填写三个模型字段，确认 Skill 目录，运行
`python -m bu_agent.cli check-skill && pytest`，再启动 Uvicorn。
