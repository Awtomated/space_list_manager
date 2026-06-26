from __future__ import annotations

from unittest.mock import MagicMock, patch

from django_hub.mixins import OrganizationMixin


class TestOrganizationMixin:
    def test_get_organization_calls_configured_callable_with_request(self):
        mock_request = MagicMock()
        mock_org = MagicMock()
        mock_fn = MagicMock(return_value=mock_org)

        mixin = OrganizationMixin()
        mixin.request = mock_request

        with patch("django_hub.mixins.get_organization_callable", return_value=mock_fn):
            result = mixin.get_organization()

        mock_fn.assert_called_once_with(mock_request)
        assert result is mock_org

    def test_get_organization_delegates_to_configured_callable(self):
        sentinel = object()
        mock_fn = MagicMock(return_value=sentinel)
        mock_request = MagicMock()

        mixin = OrganizationMixin()
        mixin.request = mock_request

        with patch("django_hub.mixins.get_organization_callable", return_value=mock_fn):
            assert mixin.get_organization() is sentinel
