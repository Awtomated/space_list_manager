from __future__ import annotations

from importlib import import_module
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULTS: dict[str, Any] = {
    "HUB_ORGANIZATION_MODEL": None,
    "HUB_GET_ORGANIZATION": None,
    "HUB_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "HUB_CONTENT_TYPE_WHITELIST": [],
    "HUB_SERIALIZERS_MAP": {},
}

REQUIRED: list[str] = [
    "HUB_ORGANIZATION_MODEL",
    "HUB_GET_ORGANIZATION",
]


def _get(name: str) -> Any:
    return getattr(settings, name, DEFAULTS.get(name))


def _import_string(dotted_path: str) -> Any:
    module_path, _, attr = dotted_path.rpartition(".")
    if not module_path:
        raise ImproperlyConfigured(f"'{dotted_path}' is not a valid dotted path.")
    module = import_module(module_path)
    try:
        return getattr(module, attr)
    except AttributeError:
        raise ImproperlyConfigured(
            f"Module '{module_path}' has no attribute '{attr}'."
        )


def get_organization_callable() -> Any:
    path: str | None = _get("HUB_GET_ORGANIZATION")
    if not path:
        raise ImproperlyConfigured(
            "HUB_GET_ORGANIZATION must be set in your settings, "
            "e.g. HUB_GET_ORGANIZATION = 'myapp.utils.get_organization'"
        )
    return _import_string(path)


def get_pagination_class() -> type:
    path: str = _get("HUB_PAGINATION_CLASS")
    return _import_string(path)


def get_content_type_whitelist() -> list:
    return _get("HUB_CONTENT_TYPE_WHITELIST") or []


def get_whitelisted_content_types() -> Any:
    from django.db.models import Q

    q: Any = Q()
    for app_label, model_name in get_content_type_whitelist():
        q |= Q(app_label=app_label, model=model_name)
    return q


def get_serializers_map() -> dict:
    raw: dict = _get("HUB_SERIALIZERS_MAP") or {}
    return {model_name: _import_string(path) for model_name, path in raw.items()}
