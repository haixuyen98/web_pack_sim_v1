from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
   path('tin-tuc/', views.articles, name='articles'),
   path('tin-tuc/c/<slug:slug>/', views.byCategory, name='category'),
   path('tin-tuc/author/<slug:author>/', views.byAuthor, name='blog_byAuthor'),
   path('tin-tuc/<slug:article>/', views.article, name='article'),
   path('tin-tuc/<slug:article>/amp/', views.article, name='article_amp'),
#    path('robots.txt', views.genRobotFile, name='seo_robots_file'),
]
