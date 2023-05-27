from django.views.generic import ListView, View
from django.shortcuts import redirect, get_object_or_404
from ..models import User, Post, TagSubscription, Tag, PostVote, UserSubscription
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin



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
@require_POST
def post_vote(request, id):
    post = get_object_or_404(Post, id=id)
    value = int(request.POST.get('value', 0))
    if value not in [-1, 1]:
        return HttpResponseBadRequest("Invalid vote value.")
    vote, created = PostVote.objects.get_or_create(post=post, user=request.user, defaults={'value': value})
    if not created:
        if vote.value == value:
            vote.delete()
        else:
            vote.value = value
            vote.save()
    post.update_vote_score()
    current_url = request.META.get('HTTP_REFERER')
    return redirect(current_url)


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
