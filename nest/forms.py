from django import forms
from .models import Post, Comment, TagSubscription, User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags', 'image']
        widgets = {
            'tags': forms.CheckboxSelectMultiple
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', 'image']

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = TagSubscription
        fields = ['tag']

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username or email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})

class UserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')
    username = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')
    karma = forms.IntegerField(required=True, widget=forms.HiddenInput(), initial=0)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'karma', 'avatar')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already taken.')
        return email