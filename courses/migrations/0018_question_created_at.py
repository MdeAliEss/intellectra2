# Generated by Django 5.1.7 on 2025-04-07 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_alter_quiz_options_remove_course_quize_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default='2025-04-07'),
            preserve_default=False,
        ),
    ]
