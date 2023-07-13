from typing import Any, Dict, Tuple
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse

class Item(models.Model):
    CATEGORIES = [
        ("Bass", "Bass"),
        ("Drums", "Drums"),
        ("Guitar", "Guitar"),
        ("Others", "Others"),
        ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=75)
    category = models.CharField(max_length=75,choices=CATEGORIES, default='Others')
    rating = models.FloatField(null=True, blank=True, default=None)
    brand = models.CharField(max_length=75, null=True)
    description = models.TextField(null=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    images = models.ImageField(upload_to="images/", default="images/default.jpg")
    slug = models.SlugField(default='', null=False)
    i_cosmetics = models.FloatField(null=True, blank=True, default=None)
    i_sound = models.FloatField(null=True, blank=True, default=None)
    i_playability = models.FloatField(null=True, blank=True, default=None)
    i_build_quality = models.FloatField(null=True, blank=True, default=None)
    favorites = models.ManyToManyField(User, related_name='favorite', default=None, blank=True)

    def recalculate_rating(self):
        reviews = self.reviews.all()
        total_score = sum([review.score for review in reviews])
        average_rating = round(float(total_score / len(reviews) if reviews else 0.0), 2)

        total_cosmetics = sum([review.r_cosmetics for review in reviews])
        average_cosmetics = round(float(total_cosmetics / len(reviews) if reviews else 0.0), 2)

        total_sound = sum([review.r_sound for review in reviews])
        average_sound = round(float(total_sound / len(reviews) if reviews else 0.0), 2)

        total_playability = sum([review.r_playability for review in reviews])
        average_playability = round(float(total_playability / len(reviews) if reviews else 0.0), 2)

        total_build_quality = sum([review.r_build_quality for review in reviews])
        average_build_quality = round(float(total_build_quality / len(reviews) if reviews else 0.0),2)

        self.rating = average_rating
        self.i_cosmetics = average_cosmetics
        self.i_sound = average_sound
        self.i_playability = average_playability
        self.i_build_quality = average_build_quality


    def __str__(self):                                          
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("item-details", kwargs={"slug": self.slug})
    


class Review(models.Model):
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User,related_name='reviewed', null=True, on_delete=models.SET_NULL)
    item_reviewed = models.ForeignKey(Item, related_name='reviews', null=True, on_delete=models.SET_NULL)
    score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True, default=0.0)
    comment = models.TextField()
    r_cosmetics = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True, default=0.0)
    r_sound = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True, default=0.0)
    r_playability = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True, default=0.0)
    r_build_quality = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True, default=0.0)
    approves = models.ManyToManyField(User, related_name='review_approves')
    
    def calculate_score(self):
        self.score = round(float((self.r_cosmetics + self.r_sound + self.r_playability + self.r_build_quality) / 4),2)

    def save(self, *args, **kwargs):
        self.calculate_score()
        super().save(*args, **kwargs)
        self.item_reviewed.recalculate_rating()
        self.item_reviewed.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.item_reviewed.recalculate_rating()
        self.item_reviewed.save()

    def __str__(self):
        return f'{self.item_reviewed} review - {self.author}'

    def get_absolute_url(self):
        return reverse("item-details", kwargs={"slug": self.item_reviewed.slug})
