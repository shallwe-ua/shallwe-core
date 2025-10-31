from typing import Any

from rest_framework import serializers
from rest_framework.fields import empty


def non_required_char_list_field() -> serializers.ListField:
    """
    serializers.ListField(
        child=serializers.CharField(
            allow_blank=False
        ),
        required=False,
        allow_empty=True
    )
    """
    return serializers.ListField(
        child=serializers.CharField(
            allow_blank=False
        ),
        required=False,
        allow_empty=True
    )


class NullStringAsNoneFieldMixin:
    """
    Convert literal 'null' (any case) to None *before* DRF's validate_empty_values(),
    so allow_null=True works at the standard place and validators are skipped.
    """
    def run_validation(self, data: type[empty] = empty) -> Any:
        if isinstance(data, str) and data.lower() == 'null':
            data = None
        # noinspection PyUnresolvedReferences
        return super().run_validation(data)


class NullParsingIntegerField(NullStringAsNoneFieldMixin, serializers.IntegerField):
    pass


class NullParsingCharField(NullStringAsNoneFieldMixin, serializers.CharField):
    pass


def non_required_null_parsing_integer_field() -> NullParsingIntegerField:
    """NullParsingIntegerField(allow_null=True, required=False)"""
    return NullParsingIntegerField(allow_null=True, required=False)


def non_required_null_parsing_char_field() -> NullParsingCharField:
    """NullParsingCharField(allow_null=True, required=False)"""
    return NullParsingCharField(allow_null=True, required=False)
