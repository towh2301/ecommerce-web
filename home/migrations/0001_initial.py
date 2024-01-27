

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('price', models.IntegerField()),
                ('category', models.CharField(choices=[('burger', 'Burger'), ('pizza', 'Pizza'), ('pasta', 'Pasta'), ('fries', 'Fries')], max_length=10)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='')),
                ('discount', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('quantity', models.IntegerField(default=1)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('price_each', models.FloatField(blank=True, null=True)),
                ('img', models.CharField(blank=True, max_length=255, null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('date_of_birth', models.DateField(default='1900-01-01')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlacedOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='waiting', max_length=255)),
                ('total_price', models.IntegerField(blank=True, null=True)),
                ('placed_order_at', models.DateTimeField(auto_now_add=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('items', models.ManyToManyField(to='home.lineitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid', models.BooleanField(default=False)),
                ('total', models.FloatField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('order_placed_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='pending', max_length=255)),
                ('items', models.ManyToManyField(to='home.lineitem')),
                ('order_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.placedorder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('ordered', models.BooleanField(default=False)),
                ('temp_address', models.CharField(blank=True, max_length=255, null=True)),
                ('items', models.ManyToManyField(to='home.lineitem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=255)),
                ('ward', models.CharField(max_length=255)),
                ('district', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('is_default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
