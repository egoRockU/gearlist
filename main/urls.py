from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from main.views import ItemDetailView

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("all/", views.all, name="all"),
    path("bass/", views.bass, name="bass"),
    path("<slug:slug>/details", ItemDetailView.as_view(), name="item-details"),
    path('fav/<int:id>/', views.add_favorite, name="add-favorite"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)