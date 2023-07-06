from django.shortcuts import render
from .models import Item
from django.views.generic import DetailView

# Create your views here.
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
        context["reviews"] = self.get_object().reviews.all()
        return context