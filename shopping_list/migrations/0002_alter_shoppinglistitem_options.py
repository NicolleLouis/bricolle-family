# Generated by Django 4.2.20 on 2025-04-04 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_list', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoppinglistitem',
            options={'permissions': [('shopping_list_access', 'Can access shopping list module')]},
        ),
    ]
