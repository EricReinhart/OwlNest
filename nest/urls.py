from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
path('', views.BestPostsListView.as_view(), name='home'),
path('login/', views.CustomLoginView.as_view(), name='login'),
path('logout/', views.CustomLogoutView.as_view(), name='logout'),
path('home/', views.BestPostsListView.as_view(), name='home'),
path('home/all/', views.BestPostsListView.as_view(), {'period': 'all'}, name='home_all'),
path('register/', views.register_request, name='register'),
path('create_post/', views.CreatePostView.as_view(), name='create_post'),
path('post_detail/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
path('edit_post/<int:pk>', views.EditPostView.as_view(), name='edit_post'),
path('delete_post/<int:pk>/', views.DeletePostView.as_view(), name='delete_post'),
path('create_comment/<int:post_pk>/', views.CreateCommentView.as_view(), name='create_comment'),
path('edit_comment/<int:pk>/', views.EditCommentView.as_view(), name='edit_comment'),
path('delete_comment/<int:pk>/', views.DeleteCommentView.as_view(), name='delete_comment'),
path('feed/', views.FeedView.as_view(), name='feed'),
path('search_posts/', views.SearchPostsView.as_view(), name='search_posts'),
path('post_vote/<int:id>/', views.post_vote, name='post_vote'),
path('user_profile/<int:pk>/', views.UserProfilePage.as_view(), name='user_profile'),
path('profile/edit/', views.edit_profile, name='edit_profile'),
path('tag/<str:tag_name>/', views.PostListView.as_view(), name='post_list'),
path('tag_subscription/', views.TagSubscriptionView.as_view(), name='tag_subscription'),
path('<int:pk>/subscribe/', views.UserSubscriptionView.as_view(), name='subscribe'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)