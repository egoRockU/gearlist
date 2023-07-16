from typing import Any, Dict, Optional
from django.shortcuts import render
from .models import Item, Review
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import ReviewForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    all_items = Item.objects.all().order_by('-date_added')
    item_paginated = Paginator(all_items, 20)
    page = request.GET.get('page')
    try:
        items = item_paginated.page(page)
    except PageNotAnInteger:
        items = item_paginated.page(1)
    except EmptyPage:
        items = item_paginated.page(item_paginated.num_pages)

    context = {
        'title': 'Home',
        'items': items,
        'item_paginated': item_paginated,
    }

    return render(request, 'main/home.html', context)

def about(request):
    context = {
        'title': 'About',
    }
    return render(request, 'main/about.html', context)

def category(request, cat):
    if cat != 'All':
        items = Item.objects.filter(category=cat).order_by('-date_added')
    else:
        items = Item.objects.all().order_by('name')
    
    item_paginated = Paginator(items, 20)

    page = request.GET.get('page')
    try:
        items = item_paginated.page(page)
    except PageNotAnInteger:
        items = item_paginated.page(1)
    except EmptyPage:
        items = item_paginated.page(item_paginated.num_pages)

    context = {
        'title': cat,
        'items': items,
        'item_paginated': item_paginated,
    }
    return render(request, 'main/category.html', context)

def rankings(request):  
    items = Item.objects.all().order_by('-rating')
    item_paginated = Paginator(items, 20)
    bass = Item.objects.filter(category='Bass').order_by('-rating')[0:10]
    drums = Item.objects.filter(category='Drums').order_by('-rating')[0:10]
    guitar = Item.objects.filter(category='Guitar').order_by('-rating')[0:10]
    others = Item.objects.filter(category='Others').order_by('-rating')[0:10]

    page = request.GET.get('page')
    try:
        items = item_paginated.page(page)
    except PageNotAnInteger:
        items = item_paginated.page(1)
    except EmptyPage:
        items = item_paginated.page(item_paginated.num_pages)

    context = {
        'title': "Top Rated",
        'items': items,
        'item_paginated': item_paginated,
        'bass': bass,
        'drums': drums,
        'guitar': guitar,
        'others': others,
    }
    return render(request, 'main/rankings.html', context)

def search_results(request):
    if request.method == "POST":
        searched = request.POST.get('item_searched')
        all_items = Item.objects.filter(name__contains=searched).order_by('-date_added')
        context = {
        'title': 'Search Results',
        'items': all_items,
        'searched': searched
        }
        return render(request, 'main/search_results.html', context)
    else:
        return HttpResponse(status=404)

class ItemDetailView(DetailView):
    model = Item
    template_name = 'main/item_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_reviews = self.get_object().reviews
        reviews = self.get_object().reviews.all()
        reviews_set = {}
        user_review = None

        if self.request.user.id != None:
            reviews = self.get_object().reviews.exclude(author=self.request.user)
            user_review = self.get_object().reviews.filter(author=self.request.user).first()

        for review in reviews:
            key = review
            if review.approves.filter(id=self.request.user.id).exists():
                value = True
                reviews_set[key] = value
            else:
                value = False
                reviews_set[key] = value
        reviews_set = tuple(reviews_set.items())

        if reviews_set != None:
            reviews_set_paginated = Paginator(reviews_set,10)
        else:
            reviews_set_paginated = None

        page = self.request.GET.get('page')
        if reviews_set_paginated != None:
            try:
                reviews_to_loop = reviews_set_paginated.page(page)
            except PageNotAnInteger:
                reviews_to_loop = reviews_set_paginated.page(1)
            except EmptyPage:
                reviews_to_loop = reviews_set_paginated.page(reviews_set_paginated.num_pages)


        context["title"] = self.get_object().name
        context["item_slug"] = self.get_object().slug
        context["user_review"] = user_review
        context["reviews"] = reviews
        context["reviews_set"] = reviews_set
        context["reviews_paginated"] = reviews_to_loop
        context["reviews_set_paginated"] = reviews_set_paginated
        context["reviews_to_loop"] = [(review, is_approved) for review, is_approved in reviews_to_loop]
        context["highlighted_review"] = all_reviews.annotate(approve_count=Count('approves')).order_by('-approve_count').first()
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

@login_required
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