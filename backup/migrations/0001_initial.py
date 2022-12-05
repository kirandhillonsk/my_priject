# Generated by Django 3.0 on 2022-09-26 15:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='backups',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(max_length=255)),
                ('Size', models.CharField(max_length=255)),
                ('create_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_schema', models.BooleanField(default=False)),
            ],
        ),
    ]