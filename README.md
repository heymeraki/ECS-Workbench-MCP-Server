# ECS Workbench MCP Server

> ECS Workbench MCP Server —— 通过阿里云 ECS Workbench 通道，让 AI 直接读写文件、执行命令、上传下载的 MCP 连接器（无需公网 IP）。

# 功能特性

| 工具 | 功能 | 备注 |
| --- | --- | --- |
| read_remote_file | 读远端文件 | 适合大文件 / 特殊字符 |
| write_remote_file | 写 / 覆盖远端文件 | 文本直写 |
| run_shell | 执行 shell 命令 | 危险命令自动拦截 |
| upload_file | 本地上传 | OSS 中转，大文件适用 |
| download_file | 远端下载到本地 | OSS 中转 |

# 环境要求
Python 3.10+、`pip install fastmcp`（或 requirements.txt）、阿里云 Workbench CLI、一个 ECS 实例。

# 快速开始
安装依赖 → 配置 CLI（`workbench config`）→ **把 `server.py` 里的 `INSTANCE_ID` 改成你的实例 ID**→ 启动 server。

# MCP 客户端接入配置（JSON 示例，用 stdio 模式）：

```
{
  "mcpServers": {
    "ecs-workbench": {
      "command": "python",
      "args": ["E:/mcp/workbench-ecs/server.py"]
    }
  }
}
```
args 参数换成本地 MCP 文件路径。

# 常见问题

- 工具全部超时 / `Access is denied` → workbench daemon 管道权限问题，用管理员身份运行一次 `workbench daemon start`（或让 MCP 进程提权）

- `connect requires an interactive terminal` → 本 server 已用非交互通道，无需 TTY

