# Generated by Django 4.2.7 on 2023-11-16 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='discount1',
            field=models.IntegerField(default=0),
        ),
    ]
