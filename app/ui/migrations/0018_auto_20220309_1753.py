# Generated by Django 3.2.4 on 2022-03-09 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0017_auto_20220309_1737'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='confdpts',
            options={'ordering': ('priority',)},
        ),
        migrations.AlterModelOptions(
            name='specdpts',
            options={'ordering': ('priority',)},
        ),
        migrations.AddField(
            model_name='confdpts',
            name='priority',
            field=models.IntegerField(default='999'),
        ),
        migrations.AddField(
            model_name='specdpts',
            name='priority',
            field=models.IntegerField(default='999'),
        ),
    ]
