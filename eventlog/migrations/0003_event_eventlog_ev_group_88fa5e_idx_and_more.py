# Generated by Django 4.2.7 on 2024-01-26 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0002_alter_event_group_alter_event_id_alter_event_message'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['group', 'timestamp'], name='eventlog_ev_group_88fa5e_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['timestamp'], name='eventlog_ev_timesta_2f8587_idx'),
        ),
    ]