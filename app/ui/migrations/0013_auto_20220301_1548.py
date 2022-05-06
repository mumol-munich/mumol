# Generated by Django 3.2.4 on 2022-03-01 15:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0012_auto_20220301_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confdpts',
            name='chipsetspec',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='confdpts_chipsetspec', to='ui.chipsetspecification'),
        ),
        migrations.AlterField(
            model_name='patientdpts',
            name='patientspec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='patientdpts_patientspec', to='ui.patientspecification'),
        ),
        migrations.AlterField(
            model_name='patientspecification',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='patientspec', to='ui.project'),
        ),
        migrations.AlterField(
            model_name='projectid',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='projectid_patient', to='ui.patient'),
        ),
        migrations.AlterField(
            model_name='sampledpts',
            name='samplespec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='sampledpts_samplespec', to='ui.samplespecification'),
        ),
        migrations.AlterField(
            model_name='samplespecification',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='samplespec', to='ui.project'),
        ),
        migrations.AlterField(
            model_name='specdpts',
            name='specification',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='specdpts_specification', to='ui.specification'),
        ),
    ]
