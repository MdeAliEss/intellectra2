# Generated by Django 5.1.7 on 2025-04-03 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_remove_course_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='pdf_file',
        ),
        migrations.RemoveField(
            model_name='course',
            name='video_file',
        ),
        migrations.AddField(
            model_name='course',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='courses/'),
        ),
        migrations.AddField(
            model_name='course',
            name='file_type',
            field=models.CharField(choices=[('pdf', 'PDF'), ('video', 'Video')], default='video', max_length=50),
        ),
    ]
