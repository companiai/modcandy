# Generated by Django 5.1.5 on 2025-02-05 07:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_remove_customuser_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCreditUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('credit_used', models.IntegerField(default=0)),
                ('credit_remaining', models.IntegerField(default=1000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_credit', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
