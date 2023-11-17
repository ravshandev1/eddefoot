# Generated by Django 4.2.5 on 2023-11-10 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_userexerciseanswer_exercise_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='feedback'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='image',
            field=models.ImageField(upload_to='lessons'),
        ),
        migrations.AlterField(
            model_name='level',
            name='icon',
            field=models.ImageField(upload_to='levels'),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to='users'),
        ),
    ]