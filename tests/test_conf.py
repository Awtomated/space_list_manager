from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

from django_hub.conf import (
    _get,
    _import_string,
    get_organization_callable,
    get_pagination_class,
)


class TestGet:
    def test_returns_setting_value(self):
        with override_settings(HUB_PAGINATION_CLASS="rest_framework.pagination.LimitOffsetPagination"):
            assert _get("HUB_PAGINATION_CLASS") == "rest_framework.pagination.LimitOffsetPagination"

    def test_returns_default_when_not_in_settings(self):
        assert _get("HUB_PAGINATION_CLASS") == "rest_framework.pagination.PageNumberPagination"

    def test_returns_none_for_unknown_key_with_no_default(self):
        assert _get("HUB_NONEXISTENT_KEY") is None


class TestImportString:
    def test_imports_valid_dotted_path(self):
        cls = _import_string("rest_framework.pagination.PageNumberPagination")
        assert cls is PageNumberPagination

    def test_raises_for_path_without_dot(self):
        with pytest.raises(ImproperlyConfigured, match="not a valid dotted path"):
            _import_string("NoDot")

    def test_raises_for_missing_attribute(self):
        with pytest.raises(ImproperlyConfigured, match="has no attribute"):
            _import_string("rest_framework.pagination.NonExistentClass")

    def test_raises_for_nonexistent_module(self):
        with pytest.raises(Exception):
            _import_string("nonexistent_module_xyz.SomeClass")


class TestGetOrganizationCallable:
    def test_raises_when_not_configured(self):
        with override_settings(HUB_GET_ORGANIZATION=None):
            with pytest.raises(ImproperlyConfigured, match="HUB_GET_ORGANIZATION"):
                get_organization_callable()

    def test_raises_when_set_to_empty_string(self):
        with override_settings(HUB_GET_ORGANIZATION=""):
            with pytest.raises(ImproperlyConfigured, match="HUB_GET_ORGANIZATION"):
                get_organization_callable()

    def test_returns_imported_callable(self):
        from django.contrib.auth import get_user_model

        fn = get_organization_callable()
        assert fn is get_user_model


class TestGetPaginationClass:
    def test_returns_default_page_number_pagination(self):
        assert get_pagination_class() is PageNumberPagination

    def test_returns_custom_class_when_overridden(self):
        with override_settings(HUB_PAGINATION_CLASS="rest_framework.pagination.LimitOffsetPagination"):
            assert get_pagination_class() is LimitOffsetPagination
