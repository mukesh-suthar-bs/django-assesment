from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import LimitOffsetPagination

from django.shortcuts import get_object_or_404

from .serializers import ArticleSerializer
from .models import Article
from .permissions import ArticleOwnerOrReadOnly

from storage.models import ImageFile
from storage.serializers import ImageFileSerializer

"""
Returns image url for repective parent content
"""


def get_content_image_url(article):
    image = ImageFile.objects.filter(
        parent_id=article.id, parent_type="article").first()
    if not image:
        return None
    return ImageFileSerializer(image).data.get('image')


"""
Deletes image entry for repective parent content
"""


def delete_content_image(article):
    image = ImageFile.objects.filter(
        parent_id=article.id, parent_type="article").first()

    if image:
        image.delete()


class ArticleListCreateView(APIView):
    """
    Create a Article Entry and Returns All the created Article Entries
    """
    permission_classes = [IsAuthenticated, ArticleOwnerOrReadOnly]
    renderer_classes = [JSONRenderer]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    # list down all the articles where articles are not in draft mode
    def get(self, request):
        articles = Article.objects.filter(draft=0)

        """
        Perform object filter based on query params
        """
        if request.query_params.get('title'):
            articles = articles.filter(
                title__contains=request.query_params.get('title'))

        if request.query_params.get('category'):
            articles = articles.filter(category=request.query_params.get('category'))

        # set pagination to articles queryset
        paginator = LimitOffsetPagination()
        articles = paginator.paginate_queryset(articles, request)

        articleSerializer = ArticleSerializer(articles, many=True)

        articles_list = articleSerializer.data

        return Response({
            'data': articles_list,
            'msg': f"{len(articles_list)} articles found"
        })

    def post(self, request):
        user = request.user
        data = request.data
        data['owner'] = user.id

        articleSerializer = ArticleSerializer(data=data)
        imageFileSerializer = None

        """
        Perfrom image validation based on paylod
        """
        if 'image' in data:
            imageFileSerializer = ImageFileSerializer(data={
                'parent_id': 0,
                'parent_type': 'article',
                'image': data['image']
            })

            imageFileSerializer.is_valid(raise_exception=True)

        if articleSerializer.is_valid(raise_exception=True):
            # save the article entry into db
            instance = articleSerializer.save()

            # get the uploaded data
            data = ArticleSerializer(instance).data

            # if image file is given and valid then save the entry into db
            # add the parent_id of recently created instance
            if imageFileSerializer:
                imageInstance = imageFileSerializer.save(
                    parent_id=data.get('id'), owner=user)
                data['image_url'] = ImageFileSerializer(
                    imageInstance).data.get('image')

            return Response({
                'data': data,
                'msg': "Article created successfully"
            })


class ArticleDetailsView(APIView):
    """
    Returns a single Article and allows update and delete of a Article
    """
    permission_classes = [IsAuthenticated, ArticleOwnerOrReadOnly]
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['article_id'])
        self.check_object_permissions(self.request, article)

        serializer = ArticleSerializer(article)
        # get image of the current article
        image_url = get_content_image_url(article)

        # prepare data
        data = serializer.data
        data['image_url'] = image_url

        return Response(data)

    def put(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['article_id'])

        # validate object have the update permission
        # ArticleOwnerOrReadOnly permission class is used
        self.check_object_permissions(self.request, article)

        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            article = serializer.save()

            return Response(ArticleSerializer(article).data)

        return Response(serializer.errors)

    def delete(self, request, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['article_id'])

        # validate object have the delete permission
        # ArticleOwnerOrReadOnly permission class is used
        self.check_object_permissions(self.request, article)

        # delete the image before deleting the content
        delete_content_image(article)
        article.delete()

        return Response({
            'msg': "Article deleted successfully"
        })
