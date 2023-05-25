from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.db.models import Q
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import DeleteView
from .forms import PostForm, CommentForm, SubscriptionForm, UserCreationForm, LoginForm
from .models import User, Post, Comment, TagSubscription, Tag, PostVote
from django.contrib.auth.views import LogoutView
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.db import models
from embed_video.backends import VideoBackend
import re
from django.db.models import Sum

class BestPostsListView(ListView):
    model = Post
    template_name = 'home.html'
    context_object_name = 'best_posts'

    def get_queryset(self):
        period = self.kwargs.get('period', 'all')
        if period == 'week':
            return Post.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(days=7)).order_by('-karma')[:10]
        elif period == 'day':
            return Post.objects.filter(created_at__gte=timezone.now()-timezone.timedelta(days=1)).order_by('-karma')[:10]
        else:
            return Post.objects.all().order_by('-karma', '-created_at')[:10]
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_posts'] = Post.objects.all().order_by('-karma')
        context['user'] = None
        context['user_rating'] = None
        context['period'] = self.kwargs.get('period', 'day')
        if not context['best_posts'].count():
            if self.kwargs.get('period', 'day') == 'week':
                message = "Sorry, there were no posts in the last week!"
            elif self.kwargs.get('period', 'day') == 'day':
                message = "Sorry, there were no posts in the last day!"
            else:
                message = "Sorry, there are no posts yet!"
            context['message'] = message
        else:
            context['message'] = ""
        if self.request.user.is_authenticated:
            context['user'] = self.request.user
            context['user_rating'] = self.request.user.karma
        return context

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_invalid(self, form):
        messages.error(self.request, 'Неправильный логин или пароль')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        login(self.request, form.get_user())
        return redirect('home')


class CustomLogoutView(LogoutView):
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)

def register_request(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = UserCreationForm()
	return render (request=request, template_name="register.html", context={"register_form":form})

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

#Youtube integration
class CustomBackend(VideoBackend):
    re_detect = re.compile(r'http://myvideo\.com/[0-9]+')
    re_code = re.compile(r'http://myvideo\.com/(?P<code>[0-9]+)')

    allow_https = False
    pattern_url = '{protocol}://play.myvideo.com/c/{code}/'
    pattern_thumbnail_url = '{protocol}://thumb.myvideo.com/c/{code}/'

    template_name = 'embed_video/custombackend_embed_code.html'  # added in v0.9

@login_required
@require_POST
def post_vote(request, id):
    post = get_object_or_404(Post, id=id)
    value = int(request.POST.get('value', 0))
    if value not in [-1, 1]:
        return HttpResponseBadRequest("Invalid vote value.")
    vote, created = PostVote.objects.get_or_create(post=post, user=request.user, defaults={'value': value})
    if not created:
        if vote.value == value:
            # User has already voted the same value
            vote.delete()
        else:
            # User has changed their vote
            vote.value = value
            vote.save()
    post.update_vote_score()
    return redirect('post_detail', pk=post.pk)

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


class CreateCommentView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Comment
    form_class = CommentForm
    success_message = "Comment created successfully."

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_pk']
        self.request.user.add_karma(1)
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        post.add_karma(1)
        return super().form_valid(form)


class EditCommentView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    success_message = "Comment updated successfully."
    template_name_suffix = '_update_form'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        return super().form_valid(form)


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


class DeleteCommentView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('home')
    success_message = "Comment deleted successfully."

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        request.user.add_karma(-self.object.karma)
        post = get_object_or_404(Post, pk=kwargs['post_pk'])
        post.add_karma(-self.object.karma)
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.kwargs['post_pk']})


class FeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        subscriptions = TagSubscription.objects.filter(user=self.request.user)
        subscribed_tags = set([subscription.tag for subscription in subscriptions])
        return Post.objects.filter(tags__in=subscribed_tags).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscriptions'] = TagSubscription.objects.filter(user=self.request.user)
        return context


@login_required
def create_subscription(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()
            messages.success(request, 'You have subscribed successfully.')
            return redirect('subscriptions')
    else:
        form = SubscriptionForm()
    return render(request, 'create_subscription.html', {'form': form})


@login_required
def delete_subscription(request, pk):
    subscription = get_object_or_404(TagSubscription, pk=pk, user=request.user)
    if request.method == 'POST':
        subscription.delete()
        messages.success(request, 'You have unsubscribed successfully.')
        return redirect('subscriptions')
    return render(request, 'delete_subscription.html', {'subscription': subscription})


@login_required
def subscriptions(request):
    subscriptions = TagSubscription.objects.filter(user=request.user)
    return render(request, 'subscriptions.html', {'subscriptions': subscriptions})


class SearchPostsView(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Post.objects.filter(Q(title__icontains=query) | Q(body__icontains=query)).order_by('-karma')
        else:
            return Post.objects.none()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context