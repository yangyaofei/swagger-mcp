"""
Data models for Swagger MCP Server
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class Parameter(BaseModel):
    """API参数模型"""
    name: str
    location: str = Field(description="参数位置: path, query, header, cookie, body")
    type: str = Field(description="参数类型")
    required: bool = False
    description: Optional[str] = None
    default: Optional[Any] = None
    example: Optional[Any] = None


class Response(BaseModel):
    """API响应模型"""
    status_code: str
    description: str
    content_type: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None


class ApiEndpoint(BaseModel):
    """API端点模型"""
    path: str
    method: str
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    parameters: List[Parameter] = Field(default_factory=list)
    responses: List[Response] = Field(default_factory=list)
    security: List[Dict[str, Any]] = Field(default_factory=list)
    deprecated: bool = False


class SchemaProperty(BaseModel):
    """Schema属性模型"""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    format: Optional[str] = None
    example: Optional[Any] = None
    enum: Optional[List[Any]] = None
    items: Optional[Dict[str, Any]] = None  # for arrays
    properties: Optional[Dict[str, Any]] = None  # for objects


class Schema(BaseModel):
    """数据模型定义"""
    name: str
    type: str
    description: Optional[str] = None
    properties: List[SchemaProperty] = Field(default_factory=list)
    required: List[str] = Field(default_factory=list)
    example: Optional[Dict[str, Any]] = None


class SwaggerInfo(BaseModel):
    """Swagger文档基本信息"""
    title: str
    version: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    contact: Optional[Dict[str, str]] = None
    license: Optional[Dict[str, str]] = None


class SwaggerDocument(BaseModel):
    """完整的Swagger文档模型"""
    info: SwaggerInfo
    apis: List[ApiEndpoint] = Field(default_factory=list)
    schemas: List[Schema] = Field(default_factory=list)
    servers: List[Dict[str, Any]] = Field(default_factory=list)
    security_definitions: Dict[str, Any] = Field(default_factory=dict) 