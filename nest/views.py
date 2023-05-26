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
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import DeleteView
from .forms import PostForm,UserForm, CommentForm, UserCreationForm, LoginForm
from .models import User, Post, Comment, TagSubscription, Tag, PostVote, UserSubscription
from django.contrib.auth.views import LogoutView
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest, Http404
from django.db import models
from embed_video.backends import VideoBackend
import re
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserChangeForm

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
        context['period'] = self.request.GET.get('period', 'best')
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

class UserProfilePage(DetailView):
   model = User
   template_name = 'user_profile.html'
   context_object_name = 'user_profile'
   def get_context_data(self, **kwargs):
       context = super().get_context_data(**kwargs)
       if self.request.user == self.get_object():
           context['edit_profile_form'] = UserChangeForm(instance=self.request.user)
       context['posts'] = Post.objects.filter(author=self.object)

       if self.request.user.is_authenticated:
           subscribed_to = UserSubscription.objects.filter(subscriber=self.request.user, subscribed_to=self.object).exists()
           context['subscribed_to'] = subscribed_to
       return context        


class UserSubscriptionView(View):
    def post(self, request, *args, **kwargs):
        subscribed_to_user = get_object_or_404(User, pk=self.kwargs['pk'])
        subscriber_user = self.request.user
        subscribed_to = request.POST.get('subscribed_to')

        if 'subscribe' in request.POST:
            UserSubscription.objects.create(subscriber=subscriber_user, subscribed_to=subscribed_to_user)
        elif 'unsubscribe' in request.POST:
            UserSubscription.objects.filter(subscriber=subscriber_user, subscribed_to=subscribed_to_user).delete()

        return redirect(reverse('user_profile', kwargs={'pk': subscribed_to_user.pk}))


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('user_profile', pk=user.pk)
    else:
        user_form = UserForm(instance=user)
    return render(request, 'edit_profile.html', {'user_form': user_form})


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
    current_url = request.META.get('HTTP_REFERER')
    return redirect(current_url)

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
    template_name = 'edit_comment.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.updated_at = timezone.now()
        response = super().form_valid(form)
        return response

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})


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

    def form_valid(self, form):
        self.object = self.get_object()
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.post.pk})


class FeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'feed.html'
    context_object_name = 'posts'

    def get_queryset(self):
        subscriptions = TagSubscription.objects.filter(user=self.request.user)
        subscribed_tags = set([subscription.tag for subscription in subscriptions])
        subscribed_users = set([subscription.subscribed_to for subscription in self.request.user.subscriptions.all()])

        return Post.objects.filter(Q(tags__in=subscribed_tags) | Q(author__in=subscribed_users)).order_by('-created_at')


class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_name = self.kwargs.get('tag_name')
        if tag_name:
            queryset = queryset.filter(tags__name=tag_name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_name = self.kwargs.get('tag_name')
        if tag_name:
            tag = Tag.objects.get(name=tag_name)
            context['tag_name'] = tag_name
            context['subscribers_count'] = tag.tagsubscription_set.count()
            if self.request.user.is_authenticated:
                context['is_subscribed'] = TagSubscription.objects.filter(user=self.request.user, tag=tag).exists()
        return context


class TagSubscriptionView(LoginRequiredMixin, ListView):
    model = TagSubscription
    template_name = 'tag_subscription.html'
    context_object_name = 'subscriptions'

    def post(self, request, *args, **kwargs):
        tag_name = request.POST.get('tag_name')
        if tag_name:
            tag = Tag.objects.get(name=tag_name)
            subscription = TagSubscription.objects.create(user=request.user, tag=tag)
        return redirect('post_list', tag_name=tag_name)


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