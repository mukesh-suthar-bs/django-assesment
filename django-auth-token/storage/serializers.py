from rest_framework import serializers

from .models import ImageFile


class ImageFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageFile
        fields = '__all__'
