from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from main.models import Item, Review
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}\'s account has been created!')
            return redirect('login')
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
        'title': 'Register',
    }
    return render(request, 'users/register.html', context)

class UserLoginView(auth_views.LoginView):
    template_name = 'users/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome {self.request.user}!')
        return response
    
@login_required
def editProfile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'title': 'Profile',
        'u_form': u_form,
        'p_form': p_form,
    }
    return render (request, 'users/editProfile.html', context)

@login_required 
def profile(request):
    context = {
        'title': 'Profile',
        'favorites': Item.objects.filter(favorites=request.user).order_by('-date_added'),
        'reviews': Review.objects.filter(author=request.user).order_by('-item_reviewed__date_added'),
    }
    return render(request, 'users/profile.html', context)

    
@login_required
def viewItems(request):
    items_added = Item.objects.filter(added_by=request.user).order_by('-date_added')
    item_paginated = Paginator(items_added, 5)
    page = request.GET.get('page')
    try:
        items = item_paginated.page(page)
    except PageNotAnInteger:
        items = item_paginated.page(1)
    except EmptyPage:
        items = item_paginated.page(item_paginated.num_pages)

    context = {
        'title': 'Item List',
        'items_added': items,
        'item_paginated': item_paginated,
    }
    return render(request, 'users/view_items.html', context)