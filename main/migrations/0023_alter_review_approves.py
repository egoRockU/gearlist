# Generated by Django 4.2.2 on 2023-07-12 08:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0022_review_approves'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='approves',
            field=models.ManyToManyField(blank=True, null=True, related_name='review_approves', to=settings.AUTH_USER_MODEL),
        ),
    ]
