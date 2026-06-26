from __future__ import annotations

from typing import Any

from rest_framework.request import Request

from django_hub.conf import get_organization_callable, get_whitelisted_content_types


class OrganizationMixin:
    """Resolves the current user's organization via HUB_GET_ORGANIZATION callable."""

    request: Request

    def get_organization(self) -> Any:
        fn = get_organization_callable()
        return fn(self.request)


class ContentTypeWhitelistMixin:
    """Provides a Q filter limiting ContentType FK choices to whitelisted models."""

    def get_whitelisted_content_types(self) -> Any:
        return get_whitelisted_content_types()
