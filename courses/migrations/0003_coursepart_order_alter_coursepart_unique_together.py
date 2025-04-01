# Generated by Django 5.1.7 on 2025-04-01 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_coursepart'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursepart',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='coursepart',
            unique_together={('course', 'order')},
        ),
    ]
