# Generated by Django 5.1.7 on 2025-04-08 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0026_question_answer_quiz_question_quiz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='quiz',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='course',
        ),
        migrations.AddField(
            model_name='course',
            name='answer',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='course',
            name='correct_answer',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='course',
            name='question',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='course',
            name='quizzes',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.DeleteModel(
            name='Answer',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='Quiz',
        ),
    ]
