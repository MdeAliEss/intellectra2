# Generated by Django 5.1.7 on 2025-04-01 16:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_chapter_delete_coursepart'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_of_contents', models.JSONField(blank=True, null=True)),
                ('extracted_text', models.TextField(blank=True, null=True)),
                ('sections', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='content', to='courses.course')),
            ],
        ),
        migrations.DeleteModel(
            name='Chapter',
        ),
    ]
