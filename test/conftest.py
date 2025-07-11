"""
pytest 配置文件 - 基本 MCP Server 测试
"""

import pytest
import pytest_asyncio
from fastmcp import Client
from swagger_mcp.server import mcp


@pytest.fixture(scope="session")
def test_swagger_url() -> str:
    """使用在线 Swagger 文档进行测试"""
    return "https://petstore.swagger.io/v2/swagger.json"


@pytest_asyncio.fixture(scope="session")
async def mcp_client():
    """创建 MCP 客户端"""
    client = Client(mcp)
    async with client:
        yield client 