from ..forms import PostForm, CommentForm
from ..models import Post,PostVote
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.db import models
from django.contrib import messages
from django.shortcuts import redirect
from django.http import Http404
import re
from embed_video.backends import VideoBackend
from django.db.models import Q



class BestPostsListView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'best_posts'

    def get_queryset(self):
        if 'period' in self.request.GET:
            period = self.request.GET['period']
            if period == 'day':
                return Post.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(days=1)).order_by('-karma')
            elif period == 'week':
                return Post.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(days=7)).order_by('-karma')
        return Post.objects.all().order_by('-karma')[:10]
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['period'] = self.request.GET.get('period','best')
        return context
    

class CreatePostView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'create_post.html'
    success_message = "Post created successfully."

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        form.save()
        return response
    
    def get_success_url(self):
        return reverse('post_detail', args=[self.object.pk])
    

class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.all().order_by('-created_at')
        context['comment_form'] = CommentForm()
        context['vote_score'] = post.votes.aggregate(models.Sum('value'))['value__sum'] or 0
        context['user_vote'] = None
        if self.request.user.is_authenticated:
            try:
                context['user_vote'] = post.votes.get(user=self.request.user).value
            except PostVote.DoesNotExist:
                pass
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added successfully.')
            return redirect('post_detail', pk=post.id)
        else:
            messages.error(request, 'Error adding comment.')
            return self.get(request, *args, **kwargs)
        

class EditPostView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "edit_post.html"
    success_message = "Your post has been updated successfully."

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        if post.author != self.request.user:
            raise Http404()
        return post
    
class DeletePostView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    success_message = "Post deleted successfully."

    def form_valid(self, form):
        post = self.get_object()
        author = post.author
        post_karma = post.karma
        author.add_karma(-post_karma)
        return super().form_valid(form)
        

class SearchPostsView(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(
            Q(title__icontains=query) | 
            Q(author__username__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(content__icontains=query)
        ).order_by('-karma')
        else:
            return Post.objects.none()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context

#Youtube integration
class CustomBackend(VideoBackend):
    re_detect = re.compile(r'http://myvideo\.com/[0-9]+')
    re_code = re.compile(r'http://myvideo\.com/(?P<code>[0-9]+)')

    allow_https = False
    pattern_url = '{protocol}://play.myvideo.com/c/{code}/'
    pattern_thumbnail_url = '{protocol}://thumb.myvideo.com/c/{code}/'

    template_name = 'embed_video/custombackend_embed_code.html'  # added in v0.9

