from rest_framework import serializers

from steepshot_io.api.models import WorkRequest


class WorkRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkRequest
        fields = '__all__'
