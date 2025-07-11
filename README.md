# Swagger MCP | OpenAPI/Swagger MCP Tool


---


An OpenAPI/Swagger document analysis tool built on [FastMCP](https://gofastmcp.com), providing clean and efficient document querying and analysis capabilities.

基于 [FastMCP](https://gofastmcp.com) 构建的 OpenAPI/Swagger 文档分析工具，提供简洁高效的文档查询和分析功能。

### 🚀 Quick Start | 快速开始

#### Method 1: Local Run | 本地运行

```bash
# Install dependencies
git clone https://github.com/username/swagger-mcp.git
cd swagger-mcp
pip install -r requirements.txt

export SWAGGER_URI="https://petstore.swagger.io/v2/swagger.json"

# Run server
fastmcp run swagger_mcp/server.py

# Or run directly
python swagger_mcp/server.py
```

#### Method 2: Docker | Docker 方式

```bash
docker run --environment \
  SWAGGER_URI=https://petstore.swagger.io/v2/swagger.json \
  --extra_hosts="host.docker.internal:host-gateway" \
  yangyaofei/swagger-mcp
```

### 🔧 Cursor IDE Integration | Cursor IDE 集成

#### Configuration | 配置

Add the following MCP configuration in Cursor 在 Cursor 中添加以下 MCP 配置:

```json
{
  "mcpServers": {
    "swagger-mcp": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### 🛠️ Available Tools | 可用工具

| Tool Name | Description |
|-----------|-------------|
| `load_swagger` | Load OpenAPI/Swagger documents |
| `get_swagger_info` | Get document basic information |
| `list_apis` | List all API endpoints |
| `get_api_details` | Get specific API details |
| `search_apis` | Search API endpoints |
| `list_schemas` | List all data models |
| `get_schema_details` | Get specific model details |


### 🛠️ 可用工具

| 工具名称 | 功能描述 |
|---------|---------|
| `load_swagger` | 加载 OpenAPI/Swagger 文档 |
| `get_swagger_info` | 获取文档基本信息 |
| `list_apis` | 列出所有 API 端点 |
| `get_api_details` | 获取特定 API 详情 |
| `search_apis` | 搜索 API 端点 |
| `list_schemas` | 列出所有数据模型 |
| `get_schema_details` | 获取特定模型详情 |

---

**Developed by Vibe Coding** 🚀 