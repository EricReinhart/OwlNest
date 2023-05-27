from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from ..forms import CommentForm
from ..models import  Post, Comment
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy



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