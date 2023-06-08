from django.urls import path
from .views import comments, post, subscription, user
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

#post

path('', post.BestPostsListView.as_view(), name='home'),
path('home/', post.BestPostsListView.as_view(), name='home'),
path('home/all/', post.BestPostsListView.as_view(), {'period': 'all'}, name='home_all'),
path('create_post/', post.CreatePostView.as_view(), name='create_post'),
path('edit_post/<int:pk>', post.EditPostView.as_view(), name='edit_post'),
path('delete_post/<int:pk>/', post.DeletePostView.as_view(), name='delete_post'),
path('search_posts/', post.SearchPostsView.as_view(), name='search_posts'),
path('post_detail/<int:pk>/', post.PostDetailView.as_view(), name='post_detail'),

#user

path('login/', user.CustomLoginView.as_view(), name='login'),
path('logout/', user.CustomLogoutView.as_view(), name='logout'),
path('register/', user.register_request, name='register'),
path('user_profile/<int:pk>/', user.UserProfilePage.as_view(), name='user_profile'),
path('profile/edit/', user.edit_profile, name='edit_profile'),

#comments

path('create_comment/<int:post_pk>/', comments.CreateCommentView.as_view(), name='create_comment'),
path('edit_comment/<int:pk>/', comments.EditCommentView.as_view(), name='edit_comment'),
path('delete_comment/<int:pk>/', comments.DeleteCommentView.as_view(), name='delete_comment'),

#subscription

path('feed/', subscription.FeedView.as_view(), name='feed'),
path('post_vote/<int:id>/', subscription.post_vote, name='post_vote'),
path('tag/<str:tag_name>/', subscription.PostListView.as_view(), name='post_list'),
path('tag_subscription/', subscription.TagSubscriptionView.as_view(), name='tag_subscription'),
path('<int:pk>/subscribe/', subscription.UserSubscriptionView.as_view(), name='subscribe'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
