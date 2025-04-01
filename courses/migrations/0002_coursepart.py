# Generated by Django 5.1.7 on 2025-03-30 22:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursePart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='courses.course')),
            ],
        ),
    ]
