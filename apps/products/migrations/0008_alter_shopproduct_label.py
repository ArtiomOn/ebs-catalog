# Generated by Django 4.1 on 2022-10-03 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_shopproduct_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopproduct',
            name='label',
            field=models.SlugField(max_length=255, primary_key=True, serialize=False),
        ),
    ]