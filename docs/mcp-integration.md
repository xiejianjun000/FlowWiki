# FlowWiki MCP 集成指南

FlowWiki MCP Server 将核心知识操作暴露为 MCP 标准工具，任何支持 MCP 的 AI Agent（Claude Code、Codex、Cursor、Gemini CLI 等）都可以直接调用。

## 工具列表

| 工具名 | 功能 | 类比 |
|--------|------|------|
| `flowwiki_index` | 读取 wiki 总索引 | `cat wiki/index.md` |
| `flowwiki_query` | 关键词搜索 wiki 页面 | `grep -r` + 相关性排序 |
| `flowwiki_read` | 读取指定 wiki 页面 | `cat wiki/concepts/ace.md` |
| `flowwiki_lint` | 运行知识库健康检查 | `python _scripts/lint.py` |
| `flowwiki_research` | 跨页面深度研究 | 手动打开 10 个文件 + 综合 |

## 接入方式

### Claude Code

在 `~/.claude/claude_desktop_config.json` 或项目的 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "flowwiki": {
      "command": "python",
      "args": ["_scripts/mcp_server.py"],
      "cwd": "/path/to/your-flowwiki"
    }
  }
}
```

### Codex / OpenAI

```json
{
  "mcpServers": {
    "flowwiki": {
      "command": "python3",
      "args": ["_scripts/mcp_server.py"],
      "cwd": "/path/to/your-flowwiki"
    }
  }
}
```

### Cursor

在 Cursor 设置 → MCP → Add Server：

- Name: `flowwiki`
- Type: `command`
- Command: `python _scripts/mcp_server.py`
- Working Directory: `/path/to/your-flowwiki`

### Docker 部署 MCP

```bash
# 构建镜像
docker compose build

# 启动 MCP 服务
docker compose --profile mcp up -d

# 查看日志
docker compose logs -f mcp-server
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 验证

```bash
# 直接测试 MCP server（stdio 模式）
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python _scripts/mcp_server.py
```

## SSE 模式（用于 Web Agent）

```bash
python _scripts/mcp_server.py --transport sse --port 8888
# 然后在浏览器访问 http://localhost:8888/sse
```

## 与竞品 MCP 对比

| 特性 | FlowWiki MCP | agentmemory MCP | SwarmVault MCP |
|------|-------------|-----------------|----------------|
| 工具数 | 5 | 9 | 6 |
| 知识检索 | 关键词+相关度排序 | BM25+向量+图谱 | BM25+向量+图谱 |
| 健康检查 | ✅ lint | ❌ | ❌ |
| 深度研究 | ✅ research | ❌ | ❌ |
| ACE 防幻觉 | ✅（通过 lint 间接） | ❌ | ❌ |
| 无外部依赖 | ✅ 纯文件系统 | ❌ 需向量库 | ❌ 需向量库 |
| 部署复杂度 | pip install mcp | pip + 向量库 | Docker + 多个服务 |
