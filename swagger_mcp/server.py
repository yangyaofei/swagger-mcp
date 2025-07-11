"""
OpenAPI/Swagger MCP Server
Supports OpenAPI 3.0 and Swagger 2.0 specifications
Built with FastMCP following the official quickstart guide
"""

from typing import Dict, Any, Optional

from fastmcp import FastMCP

# 导入解析器（已包含环境变量自动加载）
from swagger_mcp.parser import parser

# 创建 MCP 服务器实例
mcp = FastMCP("swagger-mcp")


# MCP 工具函数
@mcp.tool()
def load_swagger(source: str, source_type: str = "url") -> Dict[str, Any]:
    """加载OpenAPI/Swagger文档
    
    支持 OpenAPI 3.0 和 Swagger 2.0 规范
    
    Args:
        source: OpenAPI/Swagger文档的源（URL或文件路径）
        source_type: 源类型，"url" 或 "file"
    
    Returns:
        包含加载结果的字典
    """
    try:
        if source_type.lower() == "url":
            doc = parser.load_from_url(source)
        elif source_type.lower() == "file":
            doc = parser.load_from_file(source)
        else:
            return {
                "success": False,
                "error": f"Invalid source_type: {source_type}. Must be 'url' or 'file'"
            }
        
        return {
            "success": True,
            "message": f"Successfully loaded Swagger document: {doc.info.title}",
            "info": {
                "title": doc.info.title,
                "version": doc.info.version,
                "description": doc.info.description,
                "api_count": len(doc.apis),
                "schema_count": len(doc.schemas)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load Swagger document: {str(e)}"
        }


@mcp.tool()
def get_swagger_info() -> Dict[str, Any]:
    """获取OpenAPI/Swagger文档的基本信息
    
    Returns:
        包含文档基本信息的字典
    """
    if not parser.current_document:
        return {
            "success": False,
            "error": "No Swagger document loaded. Please load a document first."
        }
    
    doc = parser.current_document
    
    return {
        "success": True,
        "info": {
            "title": doc.info.title,
            "version": doc.info.version,
            "description": doc.info.description,
            "contact": doc.info.contact,
            "license": doc.info.license,
            "servers": doc.servers,
            "api_count": len(doc.apis),
            "schema_count": len(doc.schemas),
            "security_definitions": list(doc.security_definitions.keys()) if doc.security_definitions else []
        }
    }


@mcp.tool()
def list_apis(tag: Optional[str] = None, method: Optional[str] = None) -> Dict[str, Any]:
    """列出所有API端点
    
    Args:
        tag: 可选的标签过滤器
        method: 可选的HTTP方法过滤器
    
    Returns:
        包含API端点列表的字典
    """
    if not parser.current_document:
        return {
            "success": False,
            "error": "No Swagger document loaded. Please load a document first."
        }
    
    apis = parser.current_document.apis
    
    # 应用过滤器
    if tag:
        apis = [api for api in apis if tag.lower() in [t.lower() for t in api.tags]]
    
    if method:
        apis = [api for api in apis if api.method.lower() == method.lower()]
    
    api_list = []
    for api in apis:
        api_list.append({
            "path": api.path,
            "method": api.method,
            "summary": api.summary,
            "description": api.description,
            "tags": api.tags,
            "operation_id": api.operation_id,
            "deprecated": api.deprecated
        })
    
    return {
        "success": True,
        "apis": api_list,
        "total_count": len(api_list)
    }


@mcp.tool()
def get_api_details(path: str, method: str) -> Dict[str, Any]:
    """获取特定API端点的详细信息
    
    Args:
        path: API路径
        method: HTTP方法
    
    Returns:
        包含API详细信息的字典
    """
    if not parser.current_document:
        return {
            "success": False,
            "error": "No Swagger document loaded. Please load a document first."
        }
    
    # 查找匹配的API
    api = None
    for candidate in parser.current_document.apis:
        if candidate.path == path and candidate.method.upper() == method.upper():
            api = candidate
            break
    
    if not api:
        return {
            "success": False,
            "error": f"API not found: {method.upper()} {path}"
        }
    
    # 构建详细信息
    parameters = []
    for param in api.parameters:
        parameters.append({
            "name": param.name,
            "location": param.location,
            "type": param.type,
            "required": param.required,
            "description": param.description,
            "default": param.default,
            "example": param.example
        })
    
    responses = []
    for resp in api.responses:
        responses.append({
            "status_code": resp.status_code,
            "description": resp.description,
            "content_type": resp.content_type,
            "schema": resp.schema
        })
    
    return {
        "success": True,
        "api": {
            "path": api.path,
            "method": api.method,
            "operation_id": api.operation_id,
            "summary": api.summary,
            "description": api.description,
            "tags": api.tags,
            "parameters": parameters,
            "responses": responses,
            "security": api.security,
            "deprecated": api.deprecated
        }
    }


@mcp.tool()
def search_apis(query: str) -> Dict[str, Any]:
    """搜索API端点
    
    Args:
        query: 搜索关键词
    
    Returns:
        包含搜索结果的字典
    """
    if not parser.current_document:
        return {
            "success": False,
            "error": "No Swagger document loaded. Please load a document first."
        }
    
    results = parser.search_apis(query)
    
    api_list = []
    for api in results:
        api_list.append({
            "path": api.path,
            "method": api.method,
            "summary": api.summary,
            "description": api.description,
            "tags": api.tags,
            "operation_id": api.operation_id
        })
    
    return {
        "success": True,
        "query": query,
        "apis": api_list,
        "result_count": len(api_list)
    }


@mcp.tool()
def list_schemas() -> Dict[str, Any]:
    """列出所有数据模型Schema
    
    Returns:
        包含Schema列表的字典
    """
    if not parser.current_document:
        return {
            "success": False,
            "error": "No Swagger document loaded. Please load a document first."
        }
    
    schemas = []
    for schema in parser.current_document.schemas:
        schemas.append({
            "name": schema.name,
            "type": schema.type,
            "description": schema.description,
            "property_count": len(schema.properties),
            "required_fields": schema.required
        })
    
    return {
        "success": True,
        "schemas": schemas,
        "total_count": len(schemas)
    }


@mcp.tool()
def get_schema_details(name: str) -> Dict[str, Any]:
    """获取特定Schema的详细信息
    
    Args:
        name: Schema名称
    
    Returns:
        包含Schema详细信息的字典
    """
    if not parser.current_document:
        return {
            "success": False,
            "error": "No Swagger document loaded. Please load a document first."
        }
    
    schema = parser.get_schema_by_name(name)
    if not schema:
        return {
            "success": False,
            "error": f"Schema not found: {name}"
        }
    
    properties = []
    for prop in schema.properties:
        properties.append({
            "name": prop.name,
            "type": prop.type,
            "description": prop.description,
            "required": prop.required,
            "format": prop.format,
            "example": prop.example,
            "enum": prop.enum,
            "items": prop.items,
            "properties": prop.properties
        })
    
    return {
        "success": True,
        "schema": {
            "name": schema.name,
            "type": schema.type,
            "description": schema.description,
            "properties": properties,
            "required": schema.required,
            "example": schema.example
        }
    }
