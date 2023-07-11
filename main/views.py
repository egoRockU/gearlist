from typing import Any, Dict, Optional
from django.shortcuts import render
from .models import Item, Review
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ReviewForm


def home(request):
    context = {
        'title': 'Home',
        'items': Item.objects.all().order_by('-date_added'),
    }

    return render(request, 'main/home.html', context)

def about(request):
    context = {
        'title': 'About',
    }
    return render(request, 'main/about.html', context)

def all(request):
    context = {
        'title': 'All',
        'items': Item.objects.all().order_by('name'),
    }
    return render(request, 'main/all.html', context)

def bass(request):
    context = {
        'title': 'All',
        'items': Item.objects.filter(category='Bass').order_by('-date_added'),
    }
    return render(request, 'main/bass.html', context)


class ItemDetailView(DetailView):
    model = Item
    template_name = 'main/item_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_object().name
        context["user_review"] = self.get_object().reviews.filter(author=self.request.user).first()
        context["reviews"] = self.get_object().reviews.exclude(author=self.request.user)
        return context


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    fields = ['name', 'category', 'brand', 'description', 'images']

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class ItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Item
    fields = ['name', 'category', 'brand', 'description', 'images']

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        item = self.get_object()
        return (self.request.user == item.added_by)
            

class ItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Item
    success_url = '/'

    def test_func(self):
        item = self.get_object()
        return (self.request.user == item.added_by)
    



@login_required
def add_favorite(request, id):
    post = get_object_or_404(Item, id=id)
    if post.favorites.filter(id=request.user.id).exists():
        post.favorites.remove(request.user)
        messages.error(request, f'{post.name}  is removed from favorites')
    else:
        post.favorites.add(request.user)
        messages.success(request, f'{post.name} is added to favorites')

    return redirect('item-details', slug=post.slug)


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        slug = self.kwargs['slug']
        item = Item.objects.get(slug=slug)
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Review'
        context['item_name'] = item.name
        return context


    def form_valid(self, form):
        slug = self.kwargs['slug']
        item = Item.objects.get(slug=slug)
        form.instance.author = self.request.user
        form.instance.item_reviewed = item
        return super().form_valid(form)