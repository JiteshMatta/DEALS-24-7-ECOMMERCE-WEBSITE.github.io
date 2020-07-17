# Generated by Django 3.0.6 on 2020-05-12 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QuickShop', '0002_auto_20200510_2057'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('msg_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=70)),
                ('email', models.CharField(default='', max_length=70)),
                ('phone', models.CharField(default='', max_length=70)),
                ('desc', models.CharField(default='', max_length=500)),
            ],
        ),
    ]
