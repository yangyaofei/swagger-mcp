"""
基本 MCP 服务器测试
"""

import pytest


class TestMCPServer:
    """测试 MCP 服务器基本功能"""
    
    @pytest.mark.unit
    def test_server_creation(self):
        """测试服务器创建"""
        from swagger_mcp.server import mcp
        
        assert mcp is not None
        assert mcp.name == "swagger-mcp"
    
    @pytest.mark.unit  
    def test_server_has_tools(self):
        """测试服务器包含所有工具"""
        from swagger_mcp import server
        
        expected_tools = [
            "load_swagger",
            "get_swagger_info", 
            "list_apis",
            "get_api_details",
            "search_apis",
            "list_schemas",
            "get_schema_details"
        ]
        
        for tool_name in expected_tools:
            assert hasattr(server, tool_name), f"Tool function {tool_name} not found"
            tool_obj = getattr(server, tool_name)
            assert tool_obj is not None, f"Tool {tool_name} is None"


@pytest.mark.mcp
class TestMCPComponents:
    """测试 MCP 组件"""
    
    def test_parser_import(self):
        """测试解析器导入"""
        from swagger_mcp.parser import parser
        assert parser is not None
    
    def test_models_import(self):
        """测试模型导入"""
        from swagger_mcp.models import SwaggerDocument
        assert SwaggerDocument is not None
    
    def test_server_module_import(self):
        """测试服务器模块导入"""
        from swagger_mcp import server
        assert server is not None 