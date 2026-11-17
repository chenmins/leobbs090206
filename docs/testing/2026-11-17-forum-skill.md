# LeoBBS Skill 验证

- `quick_validate.py skills/leobbs-forum` 通过。
- 独立 agent 基线：仅给工具名称时不能确定参数；将 RATE_LIMITED 处理为等待后重试原请求，且不能从页面 URL 确定 MCP 地址。
- 加载 Skill 后，同一组场景正确生成 search_topics 的 q/mode/page，依 nextPage 翻页并读取正文；未知写入先核对、不换键；明确 429 等待后按授权最多发起一次新键尝试；页面 URL 转为 origin + /mcp，使用环境变量引用 Token。
- 验证为只读文档场景测试，没有实际发帖，也没有新建或读取真实 Token。
- 仓库版本复制到本机 Codex skills 目录，入口与连接参考内容一致。现有 MCP 配置保持原样。
