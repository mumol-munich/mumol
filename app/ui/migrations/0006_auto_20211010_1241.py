# Generated by Django 3.2.4 on 2021-10-10 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0005_auto_20211008_1955'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sample',
            name='icd10',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='location',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='mutation',
        ),
        migrations.RemoveField(
            model_name='sample',
            name='type',
        ),
    ]
