from django.urls import path

from .views import ArticleListCreateView, ArticleDetailsView

urlpatterns = [
    path('articles', ArticleListCreateView.as_view()),
    path('articles/<int:article_id>', ArticleDetailsView.as_view())
]
