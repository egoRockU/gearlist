# Generated by Django 4.2.2 on 2023-07-05 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_review_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='item_reviewed',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviews', to='main.item'),
        ),
    ]
