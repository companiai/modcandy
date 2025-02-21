# Generated by Django 5.1.5 on 2025-02-20 10:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equalizer', '0011_alter_player_playerid_alter_session_sessionid_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FlaggedMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playerName', models.CharField(blank=True, db_index=True, max_length=50)),
                ('sessionId', models.CharField(blank=True, max_length=255)),
                ('tox_type', models.CharField(blank=True, db_index=True, max_length=20)),
                ('severity', models.CharField(blank=True, db_index=True, max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('chat_message', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_flagged_message', to='equalizer.chatmessage')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_flagged_message', to='equalizer.session')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_flagged_message', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='ToxicityIncident',
        ),
    ]
