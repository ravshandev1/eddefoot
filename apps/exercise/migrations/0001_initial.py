# Generated by Django 4.2.5 on 2023-11-29 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Modul',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('name_en', models.CharField(max_length=250, null=True)),
                ('name_ru', models.CharField(max_length=250, null=True)),
                ('name_uz', models.CharField(max_length=250, null=True)),
                ('image', models.ImageField(upload_to='moduls')),
                ('ordinal_number', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='PriceOfSubscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(default=0)),
                ('description', models.TextField()),
                ('description_en', models.TextField(null=True)),
                ('description_ru', models.TextField(null=True)),
                ('description_uz', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('name_en', models.CharField(max_length=250, null=True)),
                ('name_ru', models.CharField(max_length=250, null=True)),
                ('name_uz', models.CharField(max_length=250, null=True)),
                ('image', models.ImageField(upload_to='themes')),
                ('ordinal_number', models.FloatField()),
                ('modul', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='exercise.modul')),
            ],
        ),
        migrations.AddField(
            model_name='modul',
            name='rate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moduls', to='exercise.rate'),
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('name_en', models.CharField(max_length=250, null=True)),
                ('name_ru', models.CharField(max_length=250, null=True)),
                ('name_uz', models.CharField(max_length=250, null=True)),
                ('ordinal_number', models.FloatField()),
                ('description', models.TextField(blank=True, null=True)),
                ('description_en', models.TextField(blank=True, null=True)),
                ('description_ru', models.TextField(blank=True, null=True)),
                ('description_uz', models.TextField(blank=True, null=True)),
                ('video', models.FileField(upload_to='exercises/videos')),
                ('image', models.ImageField(upload_to='exercises/images')),
                ('do_day', models.PositiveIntegerField(default=1)),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='exercise.theme')),
            ],
        ),
    ]
