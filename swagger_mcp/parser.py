"""
OpenAPI/Swagger document parser
Supports OpenAPI 3.0 and Swagger 2.0 specifications
"""

import json
import yaml
import requests
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from urllib.parse import urlparse
from openapi_spec_validator.readers import read_from_filename

from swagger_mcp.models import (
    SwaggerDocument, SwaggerInfo, ApiEndpoint, Schema, 
    Parameter, Response, SchemaProperty
)


class SwaggerParser:
    """OpenAPI/Swagger文档解析器
    
    支持解析以下格式：
    - OpenAPI 3.0 (JSON/YAML)
    - Swagger 2.0 (JSON/YAML)
    """
    
    def __init__(self):
        self.current_document: Optional[SwaggerDocument] = None
    
    def load_from_url(self, url: str) -> SwaggerDocument:
        """从URL加载OpenAPI/Swagger文档"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                spec_dict = response.json()
            elif 'application/yaml' in content_type or 'text/yaml' in content_type:
                spec_dict = yaml.safe_load(response.text)
            else:
                # 尝试JSON，如果失败则尝试YAML
                try:
                    spec_dict = response.json()
                except json.JSONDecodeError:
                    spec_dict = yaml.safe_load(response.text)
            
            self.current_document = self._parse_spec(spec_dict)
            return self.current_document
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to load Swagger document from URL: {e}")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Failed to parse Swagger document: {e}")
    
    def load_from_file(self, file_path: str) -> SwaggerDocument:
        """从本地文件加载OpenAPI/Swagger文档"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"Swagger file not found: {file_path}")
            
            # 使用openapi-spec-validator读取和验证
            spec_dict, spec_url = read_from_filename(str(path))
            
            self.current_document = self._parse_spec(dict(spec_dict))  # type: ignore
            return self.current_document
            
        except Exception as e:
            raise ValueError(f"Failed to load Swagger document from file: {e}")
    
    def validate_spec(self, spec_dict: Dict[str, Any]) -> bool:
        """验证OpenAPI规范"""
        try:
            from openapi_spec_validator import validate_spec
            validate_spec(spec_dict)  # type: ignore
            return True
        except Exception:
            return False
    
    def _parse_spec(self, spec_dict: Dict[str, Any]) -> SwaggerDocument:
        """解析OpenAPI规范字典"""
        # 解析基本信息
        info_data = spec_dict.get('info', {})
        info = SwaggerInfo(
            title=info_data.get('title', 'Unknown API'),
            version=info_data.get('version', '1.0.0'),
            description=info_data.get('description'),
            contact=info_data.get('contact'),
            license=info_data.get('license')
        )
        
        # 解析服务器信息
        servers = spec_dict.get('servers', [])
        if not servers and 'host' in spec_dict:
            # Swagger 2.0 格式
            scheme = spec_dict.get('schemes', ['http'])[0]
            base_path = spec_dict.get('basePath', '')
            servers = [{'url': f"{scheme}://{spec_dict['host']}{base_path}"}]
        
        # 解析API端点
        apis = self._parse_paths(spec_dict.get('paths', {}))
        
        # 解析数据模型
        schemas = self._parse_schemas(spec_dict)
        
        # 解析安全定义
        security_definitions = spec_dict.get('securityDefinitions', {})
        if not security_definitions:
            security_definitions = spec_dict.get('components', {}).get('securitySchemes', {})
        
        return SwaggerDocument(
            info=info,
            apis=apis,
            schemas=schemas,
            servers=servers,
            security_definitions=security_definitions
        )
    
    def _parse_paths(self, paths: Dict[str, Any]) -> List[ApiEndpoint]:
        """解析API路径"""
        apis = []
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                    continue
                
                # 解析参数
                parameters = self._parse_parameters(
                    operation.get('parameters', []) + path_item.get('parameters', [])
                )
                
                # 解析响应
                responses = self._parse_responses(operation.get('responses', {}))
                
                api = ApiEndpoint(
                    path=path,
                    method=method.upper(),
                    operation_id=operation.get('operationId'),
                    summary=operation.get('summary'),
                    description=operation.get('description'),
                    tags=operation.get('tags', []),
                    parameters=parameters,
                    responses=responses,
                    security=operation.get('security', []),
                    deprecated=operation.get('deprecated', False)
                )
                apis.append(api)
        
        return apis
    
    def _parse_parameters(self, params: List[Dict[str, Any]]) -> List[Parameter]:
        """解析参数"""
        parameters = []
        
        for param in params:
            param_type = param.get('type', 'string')
            if 'schema' in param:
                # OpenAPI 3.0 格式
                schema = param['schema']
                param_type = schema.get('type', 'string')
            
            parameter = Parameter(
                name=param['name'],
                location=param.get('in', 'query'),
                type=param_type,
                required=param.get('required', False),
                description=param.get('description'),
                default=param.get('default'),
                example=param.get('example')
            )
            parameters.append(parameter)
        
        return parameters
    
    def _parse_responses(self, responses: Dict[str, Any]) -> List[Response]:
        """解析响应"""
        response_list = []
        
        for status_code, response_data in responses.items():
            content_type = None
            schema = None
            
            # OpenAPI 3.0 格式
            if 'content' in response_data:
                for ct, content in response_data['content'].items():
                    content_type = ct
                    schema = content.get('schema')
                    break
            # Swagger 2.0 格式
            elif 'schema' in response_data:
                schema = response_data['schema']
                content_type = 'application/json'
            
            response = Response(
                status_code=status_code,
                description=response_data.get('description', ''),
                content_type=content_type,
                schema=schema
            )
            response_list.append(response)
        
        return response_list
    
    def _parse_schemas(self, spec_dict: Dict[str, Any]) -> List[Schema]:
        """解析数据模型"""
        schemas = []
        
        # OpenAPI 3.0 格式
        components = spec_dict.get('components', {})
        schemas_dict = components.get('schemas', {})
        
        # Swagger 2.0 格式
        if not schemas_dict:
            schemas_dict = spec_dict.get('definitions', {})
        
        for name, schema_def in schemas_dict.items():
            schema = self._parse_single_schema(name, schema_def)
            schemas.append(schema)
        
        return schemas
    
    def _parse_single_schema(self, name: str, schema_def: Dict[str, Any]) -> Schema:
        """解析单个数据模型"""
        properties = []
        
        for prop_name, prop_def in schema_def.get('properties', {}).items():
            property_obj = SchemaProperty(
                name=prop_name,
                type=prop_def.get('type', 'string'),
                description=prop_def.get('description'),
                required=prop_name in schema_def.get('required', []),
                format=prop_def.get('format'),
                example=prop_def.get('example'),
                enum=prop_def.get('enum'),
                items=prop_def.get('items'),
                properties=prop_def.get('properties')
            )
            properties.append(property_obj)
        
        return Schema(
            name=name,
            type=schema_def.get('type', 'object'),
            description=schema_def.get('description'),
            properties=properties,
            required=schema_def.get('required', []),
            example=schema_def.get('example')
        )
    
    def get_apis_by_tag(self, tag: str) -> List[ApiEndpoint]:
        """根据标签获取API"""
        if not self.current_document:
            return []
        
        return [api for api in self.current_document.apis if tag in api.tags]
    
    def search_apis(self, query: str) -> List[ApiEndpoint]:
        """搜索API"""
        if not self.current_document:
            return []
        
        query_lower = query.lower()
        results = []
        
        for api in self.current_document.apis:
            if (query_lower in api.path.lower() or
                query_lower in api.method.lower() or
                (api.summary and query_lower in api.summary.lower()) or
                (api.description and query_lower in api.description.lower()) or
                any(query_lower in tag.lower() for tag in api.tags)):
                results.append(api)
        
        return results
    
    def get_schema_by_name(self, name: str) -> Optional[Schema]:
        """根据名称获取Schema"""
        if not self.current_document:
            return None
        
        for schema in self.current_document.schemas:
            if schema.name == name:
                return schema
        
        return None


# 创建全局解析器实例
parser = SwaggerParser()


def load_swagger_from_env():
    """从环境变量加载 OpenAPI/Swagger 文档"""
    swagger_uri = os.getenv("SWAGGER_URI")
    if swagger_uri:
        print(f"Loading OpenAPI/Swagger document from environment: {swagger_uri}")
        try:
            if swagger_uri.startswith("http"):
                doc = parser.load_from_url(swagger_uri)
            else:
                doc = parser.load_from_file(swagger_uri)
            print(f"Successfully loaded OpenAPI/Swagger document: {doc.info.title}")
        except Exception as e:
            print(f"Warning: Failed to load OpenAPI/Swagger document from {swagger_uri}: {e}")


# 在模块加载时自动尝试加载环境变量中的文档
load_swagger_from_env() 