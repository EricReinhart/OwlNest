from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import Q


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


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
           return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to="uploads")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    karma = models.IntegerField(default=0)

    def clean(self):
        has_content = bool(self.content)
        has_image = bool(self.image)
        if not has_content and not has_image:
            raise ValidationError('Please add some content or an image.')


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