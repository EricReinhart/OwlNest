from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from embed_video.fields import EmbedVideoField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    birthday = models.DateTimeField(auto_now_add=True)
    karma = models.IntegerField(default=0)
    avatar = models.ImageField(null=True, blank=True, upload_to='uploads/')

    def add_karma(self, points):
        self.karma += points
        self.save()

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return '/static/images/default_avatar.jpg'
        
class UserSubscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
           return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    karma = models.IntegerField(default=0)
    media = models.FileField(upload_to="uploads", blank=True)
    video = EmbedVideoField(blank=True)
    users = models.ManyToManyField(User, related_name='posts')

    def clean(self):
        has_content = bool(self.content)
        has_media = bool(self.media) or bool(self.video)
        if not has_content and not has_media:
            raise ValidationError('Please add some content or upload a media file or provide a media URL.')
        
        if not self.title:
            raise ValidationError('Please provide a title for the post.')

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    @property
    def total_votes(self):
        return self.votes.aggregate(models.Sum('value'))['value__sum'] or 0

    def user_vote(self, user):
        try:
            return self.votes.get(user=user).value
        except PostVote.DoesNotExist:
            return None

    def update_vote_score(self):
        total_votes = self.total_votes
        self.karma = total_votes
        self.save()

        if total_votes > 0 and self.author != self.votes.last().user:
            self.author.add_karma(1)


class PostVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField(choices=[(-1, '-1'), (1, '1')])

    class Meta:
        unique_together = ['user', 'post']


class Comment(models.Model):
    content = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    image = models.ImageField(upload_to="uploads", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        has_content = bool(self.content)
        has_image = bool(self.image)
        if not has_content and not has_image:
            raise ValidationError('Please add some content or an image.')


class CommentVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField(choices=[(-1, '-1'), (1, '1')])

    class Meta:
        unique_together = ['user', 'comment']


class TagSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} subscribed to {self.tag.name}"