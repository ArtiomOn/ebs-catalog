# Generated by Django 4.1 on 2022-10-07 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_alter_shopproduct_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shopproduct',
            options={'ordering': ['-label'], 'verbose_name': 'Shop product', 'verbose_name_plural': 'Shop products'},
        ),
    ]