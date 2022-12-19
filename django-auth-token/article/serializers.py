from rest_framework import serializers

from .models import Article


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {
            'created_at': {
                'read_only': True
            },
            'modified_at': {
                'read_only': True
            },
            'owner': {
                'write_only': True
            }
        }
