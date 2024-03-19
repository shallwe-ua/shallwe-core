from rest_framework import serializers

from ..models import UserProfile


class UserProfileVisibilitySerializer(serializers.ModelSerializer):
    is_hidden = serializers.BooleanField(required=True)

    class Meta:
        model = UserProfile
        fields = ['is_hidden']
