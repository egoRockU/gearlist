from typing import Any, Dict, Optional
from django.shortcuts import render
from .models import Item, Review
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ReviewForm
from django.http import HttpResponseRedirect
from django.urls import reverse

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
        reviews = self.get_object().reviews.exclude(author=self.request.user)
        approved = False
        for review in reviews:
            if review.approves.filter(id=self.request.user.id).exists():
                approved = True
            else:
                approved = False

        context["title"] = self.get_object().name
        context["item_slug"] = self.get_object().slug
        context["user_review"] = self.get_object().reviews.filter(author=self.request.user).first()
        context["reviews"] = reviews
        context["is_approved"] = approved
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


def approve(request, slug, id):
    review = get_object_or_404(Review, id=id)
    item = get_object_or_404(Item, slug=slug)
    if review.approves.filter(id=request.user.id).exists():
        review.approves.remove(request.user)
    else:
        review.approves.add(request.user)
    return HttpResponseRedirect(reverse('item-details', args=[item.slug]) + f'#{id}')


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        slug = self.kwargs['slug']
        item = Item.objects.get(slug=slug)
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Review'
        context['form_legend'] = 'Add Review for'
        context['item_name'] = item.name
        return context

    def form_valid(self, form):
        slug = self.kwargs['slug']
        item = Item.objects.get(slug=slug)
        form.instance.author = self.request.user
        form.instance.item_reviewed = item
        return super().form_valid(form)
    

class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        id = self.kwargs['pk']
        review = Review.objects.get(id=id)
        item_review = review.item_reviewed
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Review'
        context['form_legend'] = 'Edit Review for'
        context['item_name'] = item_review.name
        return context
    
    
    def test_func(self):
        review = self.get_object()
        return (self.request.user == review.author)
    

class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    success_url = '/'

    def get_context_data(self, **kwargs):
        id = self.kwargs['pk']
        review = Review.objects.get(id=id)
        item_review = review.item_reviewed
        context = super().get_context_data(**kwargs)
        context['item_reviewed'] = item_review
        return context

    def test_func(self):
        review = self.get_object()
        return (self.request.user == review.author)