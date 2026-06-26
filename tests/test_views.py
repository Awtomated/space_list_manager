from __future__ import annotations

from unittest.mock import patch

import pytest
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from django_hub.views import (
    BaseListItemsViewset,
    BaseListViewset,
    BaseFolderViewset,
    BaseSpaceListViewset,
    BaseSpaceViewset,
)

SEARCHABLE_VIEWSETS = [
    BaseSpaceViewset,
    BaseFolderViewset,
    BaseSpaceListViewset,
    BaseListViewset,
]
ALL_VIEWSETS = SEARCHABLE_VIEWSETS + [BaseListItemsViewset]


class TestPermissions:
    @pytest.mark.parametrize("vs_class", ALL_VIEWSETS, ids=lambda c: c.__name__)
    def test_requires_authentication(self, vs_class):
        assert IsAuthenticated in vs_class.permission_classes


class TestSearchFilter:
    @pytest.mark.parametrize("vs_class", SEARCHABLE_VIEWSETS, ids=lambda c: c.__name__)
    def test_has_search_filter_backend(self, vs_class):
        assert filters.SearchFilter in vs_class.filter_backends

    @pytest.mark.parametrize("vs_class", SEARCHABLE_VIEWSETS, ids=lambda c: c.__name__)
    def test_searches_by_name(self, vs_class):
        assert "name" in vs_class.search_fields

    def test_list_items_viewset_has_no_search_filter(self):
        assert "filter_backends" not in BaseListItemsViewset.__dict__


class TestPaginationClass:
    @pytest.mark.parametrize("vs_class", ALL_VIEWSETS, ids=lambda c: c.__name__)
    def test_pagination_class_property_returns_configured_class(self, vs_class):
        vs = vs_class.__new__(vs_class)
        with patch("django_hub.views.get_pagination_class", return_value=PageNumberPagination):
            assert vs.pagination_class is PageNumberPagination
