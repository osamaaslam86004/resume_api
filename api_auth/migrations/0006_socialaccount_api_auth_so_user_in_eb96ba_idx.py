# Generated by Django 4.2.8 on 2024-03-19 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_auth', '0005_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='socialaccount',
            index=models.Index(fields=['user_info', 'access_token', 'code'], name='api_auth_so_user_in_eb96ba_idx'),
        ),
    ]
