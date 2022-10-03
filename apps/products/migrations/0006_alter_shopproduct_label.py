# Generated by Django 4.1 on 2022-09-30 12:52

from django.db import migrations
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_shopproduct_attachments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopproduct',
            name='label',
            field=django_extensions.db.fields.AutoSlugField(allow_duplicates=True, blank=True, editable=False, populate_from=('shop__title', 'title', 'description'), primary_key=True, serialize=False),
        ),
    ]