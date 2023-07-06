# Generated by Django 4.2.2 on 2023-06-23 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.CharField(max_length=75, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='rating',
            field=models.FloatField(null=True),
        ),
    ]
