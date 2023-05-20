from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
path('', views.BestPostsListView.as_view(), name='home'),
path('home/str:period/', views.BestPostsListView.as_view(), name='home_period'),
path('home/all/', views.BestPostsListView.as_view(), {'period': 'all'}, name='home_all'),
path('register/', views.RegisterView.as_view(), name='register'),
path('create_post/', views.CreatePostView.as_view(), name='create_post'),
path('edit_post/int:pk/', views.EditPostView.as_view(), name='edit_post'),
path('delete_post/int:pk/', views.DeletePostView.as_view(), name='delete_post'),
path('create_comment/int:post_pk/', views.CreateCommentView.as_view(), name='create_comment'),
path('edit_comment/int:pk/', views.EditCommentView.as_view(), name='edit_comment'),
path('delete_comment/int:pk/', views.DeleteCommentView.as_view(), name='delete_comment'),
path('create_subscription/', views.create_subscription, name='create_subscription'),
path('delete_subscription/int:pk/', views.delete_subscription, name='delete_subscription'),
path('subscriptions/', views.subscriptions, name='subscriptions'),
path('feed/', views.FeedView.as_view(), name='feed'),
path('search_posts/', views.SearchPostsView.as_view(), name='search_posts'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)