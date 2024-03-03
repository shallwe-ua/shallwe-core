from rest_framework import serializers


def non_required_char_list_field():
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
