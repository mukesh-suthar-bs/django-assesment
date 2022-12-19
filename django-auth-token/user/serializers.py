from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueValidator

from random_username.generate import generate_username


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'password', 'password2', 'email']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'username': {
                'required': False
            },
            'email': {
                'required': True
            }
        }

    def validate(self, attrs):
        """
            password checking
        """
        if not self.instance and attrs['password'] != attrs['password2']:
            raise ValidationError({"password": "Password field dosen't match"})

        return super().validate(attrs)

    def create(self, validated_data):
        username = ''

        if 'username' in validated_data:
            username = validated_data['username']
        else:
            username = generate_username(1).pop()

        user = User.objects.create(
            username=username,
            email=validated_data['email']
        )

        # set first name and last name if given
        if 'first_name' in validated_data:
            user.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            user.last_name = validated_data['last_name']

        user.set_password(validated_data['password'])
        user.save()
        return user
