# Generated by Django 4.2.2 on 2023-07-07 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_alter_item_i_build_quality_alter_item_i_cosmetics_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('Bass', 'Bass'), ('Drums', 'Drums'), ('Guitar', 'Guitar'), ('Others', 'Others')], default='Others', max_length=75),
        ),
    ]