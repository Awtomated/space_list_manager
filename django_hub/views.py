from __future__ import annotations

import operator
from functools import reduce

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, models
from rest_framework import filters, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated

from django_hub.conf import get_pagination_class, get_serializers_map
from django_hub.mixins import OrganizationMixin


class BaseSpaceViewset(OrganizationMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    SPACE_MODEL = None
    SHARED_SPACE_MODEL = None

    @property
    def pagination_class(self) -> type:
        return get_pagination_class()

    def get_queryset(self):
        user = self.request.user
        shared_ids = self.SHARED_SPACE_MODEL.objects.filter(user=user).values_list("space_id", flat=True)
        return self.SPACE_MODEL.objects.filter(
            models.Q(created_by=user) | models.Q(id__in=shared_ids)
        ).distinct()

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except IntegrityError:
            raise ValidationError({"detail": "A space with this name already exists for your account."})


class BaseFolderViewset(OrganizationMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    SPACE_MODEL = None
    FOLDER_MODEL = None
    SHARED_SPACE_MODEL = None
    SHARED_FOLDER_MODEL = None

    @property
    def pagination_class(self) -> type:
        return get_pagination_class()

    def get_queryset(self):
        user = self.request.user
        params = self.request.query_params
        _type = (params.get("type") or "").lower()
        _id = params.get("id")

        if _type == "shared":
            shared_ids = self.SHARED_FOLDER_MODEL.objects.filter(user=user).values_list("folder_id", flat=True)
            return self.FOLDER_MODEL.objects.filter(id__in=shared_ids).distinct()

        space_owned = self.SPACE_MODEL.objects.filter(created_by=user, id=_id).exists()
        space_shared = self.SHARED_SPACE_MODEL.objects.filter(user=user, space_id=_id).exists()
        if space_owned or space_shared:
            return self.FOLDER_MODEL.objects.filter(space_id=_id).distinct()
        return self.FOLDER_MODEL.objects.none()

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except IntegrityError:
            raise ValidationError({"detail": "A folder with this name already exists for your account."})


class BaseSpaceListViewset(OrganizationMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    SPACE_MODEL = None
    LIST_MODEL = None

    @property
    def pagination_class(self) -> type:
        return get_pagination_class()

    def get_queryset(self):
        user = self.request.user
        _id = self.request.query_params.get("id")
        if _id:
            return self.LIST_MODEL.objects.filter(space_id=_id).distinct()
        return self.LIST_MODEL.objects.filter(created_by=user).distinct()

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except IntegrityError:
            raise ValidationError({"detail": "A list with this name already exists."})


class BaseListViewset(OrganizationMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    SPACE_MODEL = None
    FOLDER_MODEL = None
    LIST_MODEL = None
    LIST_GROUP_MODEL = None
    SHARED_LIST_MODEL = None

    @property
    def pagination_class(self) -> type:
        return get_pagination_class()

    def get_queryset(self):
        params = self.request.query_params
        _type_raw = params.get("type")
        _type = _type_raw.lower() if _type_raw else None
        _id = params.get("id")

        user = self.request.user

        if _type == "shared":
            shared_ids = self.SHARED_LIST_MODEL.objects.filter(user=user).values_list("list_id", flat=True)
            return self.LIST_MODEL.objects.filter(id__in=shared_ids).distinct()

        if _type is None and _id is None:
            space_ct = ContentType.objects.get_for_model(self.SPACE_MODEL)
            folder_ct = ContentType.objects.get_for_model(self.FOLDER_MODEL)
            return self.LIST_MODEL.objects.filter(created_by=user).exclude(
                group_memberships__content_type__in=[space_ct, folder_ct]
            ).distinct()

        _type_to_model = {
            "space": self.SPACE_MODEL,
            "folder": self.FOLDER_MODEL,
            "list": self.LIST_MODEL,
        }
        model = _type_to_model.get(_type)
        content_type = ContentType.objects.get_for_model(model)
        return self.LIST_MODEL.objects.filter(
            group_memberships__content_type=content_type,
            group_memberships__object_id=_id,
        ).distinct()

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except IntegrityError:
            raise ValidationError({"detail": "A list with this name already exists in your account."})


class BaseListItemsViewset(OrganizationMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    LIST_MODEL = None
    LIST_ITEM_MODEL = None

    @property
    def pagination_class(self) -> type:
        return get_pagination_class()

    def get_queryset(self):
        _id = self.request.query_params.get("id")
        try:
            parent_list = self.LIST_MODEL.objects.get(id=_id)
        except ObjectDoesNotExist:
            raise NotFound("The specified list does not exist.")

        target_model = parent_list.content_type.model_class()

        if parent_list.type == "static":
            item_ids = self.LIST_ITEM_MODEL.objects.filter(list=parent_list).values_list("object_id", flat=True)
            return target_model.objects.filter(id__in=item_ids)

        # dynamic: apply filters JSONField as combined OR query
        filters_value = (parent_list.filters or {}).get("filters")
        if not filters_value:
            return target_model.objects.none()
        q_list = [models.Q(**{k: v}) for k, v in filters_value.items()]
        return target_model.objects.filter(reduce(operator.or_, q_list))

    def get_serializer_class(self):
        if self.action == "list":
            _id = self.request.query_params.get("id")
            if _id:
                try:
                    parent_list = self.LIST_MODEL.objects.get(id=_id)
                    model_name = parent_list.content_type.model
                    serializer_cls = get_serializers_map().get(model_name)
                    if serializer_cls:
                        return serializer_cls
                except (ObjectDoesNotExist, AttributeError):
                    pass
        return super().get_serializer_class()
