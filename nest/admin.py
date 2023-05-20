from django.contrib import admin
from .models import User, Post, Comment, TagSubscription, Tag

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(TagSubscription)
admin.site.register(Tag)