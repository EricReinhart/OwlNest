from ..forms import UserForm, UserCreationForm, LoginForm
from ..models import User, Post, UserSubscription
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout, login
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm



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
		form = UserCreationForm(request.POST, request.FILES)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("home")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = UserCreationForm()
	return render (request=request, template_name="register.html", context={"register_form":form})


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