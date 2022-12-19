from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.contrib.auth.models import User

from .serializers import UserSerializer
from .permissions import IsOwnerOrAdmin
from storage.serializers import ImageFileSerializer


"""
Generate access auth token 
"""


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


class Signup(APIView):
 
    renderer_classes = [JSONRenderer]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        imageFileSerializer = None

        # check if image is uploaded
        if 'image' in data:
            imageFileSerializer = ImageFileSerializer(data={
                'parent_id': 0,
                'parent_type': 'user',
                'image': data['image']
            })

            imageFileSerializer.is_valid(raise_exception=True)

        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            token = get_tokens_for_user(instance)

            data = UserSerializer(instance).data

            # if image file is given and valid then save the entry
            if imageFileSerializer:
                imageInstance = imageFileSerializer.save(
                    parent_id=data.get('id'))
                data['image_url'] = ImageFileSerializer(
                    imageInstance).data.get('image')

            response_data = {
                'data': data,
                'token': token
            }
            return Response(response_data)

        return Response(serializer.errors)


class UserList(RetrieveUpdateDestroyAPIView):
    """
    Returns a single User and allows updates and deletion of User.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsOwnerOrAdmin]
    lookup_url_kwarg = 'pk'
