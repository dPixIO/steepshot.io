from rest_framework.generics import CreateAPIView

from dpix_io.api import serializers


class WorkRequestAPIView(CreateAPIView):
    serializer_class = serializers.WorkRequestSerializer
