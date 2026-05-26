"""Shared drf-spectacular schema helpers."""
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

DetailResponseSerializer = inline_serializer(
    'DetailResponse',
    fields={'detail': serializers.CharField()},
)
