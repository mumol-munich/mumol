# Generated by Django 3.2.4 on 2022-03-29 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0020_auto_20220329_1401'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sample',
            unique_together={('projectid', 'dateofreceipt', 'visit')},
        ),
    ]
