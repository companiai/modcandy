# Generated by Django 5.1.5 on 2025-01-24 04:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equalizer', '0005_remove_badwordshortform_real_form'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_chat_message', to='equalizer.session'),
        ),
        migrations.CreateModel(
            name='ToxicityIncident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playerName', models.CharField(blank=True, db_index=True, max_length=50)),
                ('sessionId', models.CharField(db_index=True, max_length=255, unique=True)),
                ('tox_type', models.CharField(blank=True, db_index=True, max_length=20)),
                ('severity', models.CharField(blank=True, db_index=True, max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('chat_message', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_toxicity_incident', to='equalizer.chatmessage')),
            ],
        ),
    ]
