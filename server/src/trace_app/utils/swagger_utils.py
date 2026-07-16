import inspect
from typing import List, Type, Dict, Any, get_type_hints, Tuple

import yaml
from tornado_request_mapping import RequestMapping, request_mapping
from typing_extensions import TypedDict

from trace_app.common.base_handler import BaseHandler


class BaseResponse(TypedDict):
    code: str
    info: str


class StringResponse(BaseResponse):
    data: str


class PageItem(TypedDict):
    total: int
    page: int
    page_size: int
    list: List[Any]


class ListResponse(BaseResponse):
    data: PageItem


def _is_typed_dict(cls) -> bool:
    return hasattr(cls, '__annotations__') and isinstance(cls, type) and issubclass(cls, dict)


def _typed_dict_to_schema(cls) -> Dict[str, Any]:
    properties = {}
    field_comments = {}

    try:
        source = inspect.getsource(cls)
        class_lines = source.split('\n')
        for line in class_lines:
            line = line.strip()
            if ':' in line and '#' in line:
                field_part = line.split(':')[0].strip()
                comment_part = line.split('#')[1].strip()
                field_comments[field_part] = comment_part
    except Exception:
        pass

    parent_class_name = None
    try:
        source = inspect.getsource(cls)
        class_def_line = source.split('\n')[0].strip()
        if '(' in class_def_line and ')' in class_def_line:
            parent_part = class_def_line.split('(')[1].split(')')[0]
            parent_class_name = parent_part.strip()
    except Exception:
        pass

    if parent_class_name and parent_class_name != 'TypedDict':
        try:
            module = inspect.getmodule(cls)
            if module:
                if hasattr(module, parent_class_name):
                    parent_cls = getattr(module, parent_class_name)
                    parent_schema = _typed_dict_to_schema(parent_cls)
                    if 'properties' in parent_schema:
                        for prop_name, prop_details in parent_schema['properties'].items():
                            if 'description' in prop_details and prop_name not in field_comments:
                                field_comments[prop_name] = prop_details['description']
        except Exception:
            pass

    annotations = get_type_hints(cls)

    for field_name, field_type in annotations.items():
        origin_type = getattr(field_type, '__origin__', None)

        if field_type == str:
            field_schema = {"type": "string"}
        elif field_type == int:
            field_schema = {"type": "integer"}
        elif field_type == float:
            field_schema = {"type": "number"}
        elif field_type == bool:
            field_schema = {"type": "boolean"}
        elif origin_type == List:
            item_type = field_type.__args__[0]
            if _is_typed_dict(item_type):
                field_schema = {
                    "type": "array",
                    "items": _typed_dict_to_schema(item_type)
                }
            elif item_type == str:
                field_schema = {
                    "type": "array",
                    "items": {"type": "string"}
                }
            else:
                field_schema = {
                    "type": "array",
                    "items": {"type": "string"}
                }
        elif _is_typed_dict(field_type):
            field_schema = _typed_dict_to_schema(field_type)
        else:
            field_schema = {"type": "string"}

        if field_name in field_comments:
            field_schema["description"] = field_comments[field_name]

        properties[field_name] = field_schema

    return {
        "type": "object",
        "properties": properties
    }


def swagger_doc(
        tags: List[str] = None,
        summary: str = None,
        description: str = None,
        request_model: Type[TypedDict] = None,
        response_model: Type[TypedDict] = None,
        content_type: str = None,
):
    def decorator(func):
        doc = {
            "tags": tags or [],
            "summary": summary or "",
            "description": description or ""
        }

        if request_model:
            request_method = ""
            if hasattr(func, 'request_mapping'):
                request_method = func.request_mapping.method.lower()

            is_query_param_method = (request_method in ('get', 'delete')) or \
                                   (func.__name__.startswith('create_') and request_method == 'get')

            if content_type == "multipart/form-data":
                schema = _typed_dict_to_schema(request_model)
                doc["parameters"] = []
                if 'properties' in schema:
                    for prop_name, prop_details in schema['properties'].items():
                        param = {
                            "in": "formData",
                            "name": prop_name,
                            "description": prop_details.get('description', ''),
                            "required": prop_name in schema.get('required', []),
                            "type": prop_details.get('type', 'string')
                        }
                        if prop_name == 'file':
                            param["type"] = "file"
                        doc["parameters"].append(param)
                doc["consumes"] = ["multipart/form-data"]
            elif is_query_param_method:
                schema = _typed_dict_to_schema(request_model)
                doc["parameters"] = []
                if 'properties' in schema:
                    for prop_name, prop_details in schema['properties'].items():
                        param = {
                            "in": "query",
                            "name": prop_name,
                            "description": prop_details.get('description', ''),
                            "required": prop_name in schema.get('required', []),
                            "schema": {"type": prop_details.get('type', 'string')}
                        }
                        doc["parameters"].append(param)
            else:
                schema = _typed_dict_to_schema(request_model)
                doc["parameters"] = [{
                    "in": "body",
                    "name": "body",
                    "description": "请求参数",
                    "required": True,
                    "schema": schema
                }]
                if content_type:
                    doc["consumes"] = [content_type]

        if response_model:
            schema = _typed_dict_to_schema(response_model)
            doc["responses"] = {
                "200": {
                    "description": "成功",
                    "schema": schema
                }
            }

        yaml_doc = "---\n" + yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True)
        func.__doc__ = yaml_doc
        return func

    return decorator


def generate_handler_classes(base_cls) -> List[Tuple[str, type, str]]:
    routes = []
    cls_url = getattr(base_cls, 'request_mapping', None).value
    for name, func in inspect.getmembers(base_cls, predicate=inspect.isfunction):
        mapping: RequestMapping = getattr(func, 'request_mapping', None)
        if not mapping:
            continue
        method_type = mapping.method.lower()
        path = mapping.value
        method_name = method_type if method_type in ('get', 'post', 'put', 'delete') else 'get'
        classname = base_cls.__name__

        original_doc = func.__doc__ or "No docstring provided"

        is_query_param_method = (method_type in ('get', 'delete')) or \
                               (func.__name__.startswith('create_') and method_type == 'get')

        if is_query_param_method and original_doc:
            try:
                doc_yaml = yaml.safe_load(original_doc.replace('---\n', ''))
                if 'parameters' in doc_yaml and isinstance(doc_yaml['parameters'], list):
                    for i, param in enumerate(doc_yaml['parameters']):
                        if param.get('in') == 'body' and 'schema' in param:
                            schema = param['schema']
                            new_params = []
                            if 'properties' in schema:
                                for prop_name, prop_details in schema['properties'].items():
                                    query_param = {
                                        "in": "query",
                                        "name": prop_name,
                                        "description": prop_details.get('description', ''),
                                        "required": prop_name in schema.get('required', []),
                                        "schema": {"type": prop_details.get('type', 'string')}
                                    }
                                    new_params.append(query_param)
                            doc_yaml['parameters'] = new_params
                            original_doc = "---\n" + yaml.dump(doc_yaml, default_flow_style=False, sort_keys=False, allow_unicode=True)
                            break
            except Exception:
                pass

        attrs = {
            '__doc__': original_doc,
            method_name: func,
        }

        handler_cls = type(classname, (BaseHandler,), attrs)
        handler_cls = request_mapping(cls_url)(handler_cls)

        doc = getattr(handler_cls, method_name).__doc__ or original_doc
        if doc != original_doc:
            setattr(getattr(handler_cls, method_name), '__doc__', original_doc)

        routes.append((path, handler_cls, method_type))

    return routes
