# Generated by Django 5.1.5 on 2025-04-25 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
