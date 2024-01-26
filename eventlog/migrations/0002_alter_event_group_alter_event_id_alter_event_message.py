# Generated by Django 4.2.7 on 2024-01-26 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='group',
            field=models.CharField(max_length=40, verbose_name='Event Group'),
        ),
        migrations.AlterField(
            model_name='event',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='event',
            name='message',
            field=models.TextField(verbose_name='Message'),
        ),
    ]