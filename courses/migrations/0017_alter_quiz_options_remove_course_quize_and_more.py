# Generated by Django 5.1.7 on 2025-04-07 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0016_alter_course_id_quiz'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='quiz',
            options={},
        ),
        migrations.RemoveField(
            model_name='course',
            name='quize',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='correct_answer',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='options',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='order',
        ),
        migrations.RemoveField(
            model_name='quiz',
            name='question',
        ),
        migrations.AddField(
            model_name='quiz',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default='2025-04-07'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quiz',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='quiz',
            name='passing_score',
            field=models.PositiveIntegerField(default=70, help_text='Minimum score percentage to pass the quiz'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='time_limit',
            field=models.PositiveIntegerField(default=0, help_text='Time limit in minutes (0 for no limit)'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='title',
            field=models.CharField(default='2025-04-07', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('correct_answer_id', models.PositiveIntegerField(blank=True, null=True)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='courses.quiz')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='courses.question')),
            ],
        ),
    ]
