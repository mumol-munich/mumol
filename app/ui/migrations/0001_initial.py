# Generated by Django 3.2.4 on 2021-10-08 09:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9_\\- ]+$', 'Only alphanumeric characters, -, _ and space are allowed')])),
            ],
        ),
        migrations.CreateModel(
            name='ChipsetSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('manufacturer', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DatapointType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9_\\- ]+$', 'Only alphanumeric characters, -, _ and space are allowed')])),
                ('type', models.CharField(choices=[('integer', 'integer'), ('numeric', 'numeric'), ('varchar', 'varchar'), ('boolean', 'boolean'), ('select', 'select'), ('multiple', 'multiple')], default='varchar', max_length=32)),
                ('helptext', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('options', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('rcmd_methods', models.ManyToManyField(editable=False, related_name='rcmd_methods', to='ui.AnalysisMethod')),
            ],
        ),
        migrations.CreateModel(
            name='DatapointValidator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validator', models.CharField(choices=[('regex', 'RegexValidator'), ('email', 'EmailValidator'), ('maxval', 'MaxValueValidator'), ('minval', 'MinValueValidator'), ('maxlen', 'MaxLengthValidator'), ('minlen', 'MinLengthValidator'), ('decval', 'DecimalValidator')], max_length=32)),
                ('value', models.CharField(max_length=255)),
                ('errormessage', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=255)),
                ('lastname', models.CharField(max_length=255)),
                ('dateofbirth', models.DateField(verbose_name='Date of Birth')),
            ],
            options={
                'unique_together': {('firstname', 'lastname', 'dateofbirth')},
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9_\\- ]+$', 'Only alphanumeric characters, -, _ and space are allowed')])),
                ('users', models.ManyToManyField(related_name='project_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectId',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projectid', models.CharField(max_length=255)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projectid_patient', to='ui.patient')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='projectid_project', to='ui.project')),
            ],
            options={
                'unique_together': {('project', 'patient', 'projectid'), ('project', 'projectid')},
            },
        ),
        migrations.CreateModel(
            name='Specification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=255, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9_\\- ]+$', 'Only alphanumeric characters, -, _ and space are allowed')])),
                ('name', models.CharField(max_length=255)),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='specification_gene', to='ui.gene')),
                ('method', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='specification_method', to='ui.analysismethod')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='specification_project', to='ui.project')),
            ],
            options={
                'unique_together': {('project', 'gene', 'method', 'status')},
            },
        ),
        migrations.CreateModel(
            name='SpecDPTs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mandatory', models.BooleanField(default=False)),
                ('default', models.CharField(blank=True, max_length=1000, null=True)),
                ('datapointtype', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='specdpts_datapointtype', to='ui.datapointtype')),
                ('specification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specdpts_specification', to='ui.specification')),
            ],
            options={
                'unique_together': {('specification', 'datapointtype')},
            },
        ),
        migrations.CreateModel(
            name='SampleSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='samplespec_project', to='ui.project')),
            ],
        ),
        migrations.CreateModel(
            name='SampleDPTs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mandatory', models.BooleanField(default=False)),
                ('default', models.CharField(blank=True, max_length=1000, null=True)),
                ('datapointtype', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='sampledpts_datapointtype', to='ui.datapointtype')),
                ('samplespec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sampledpts_samplespec', to='ui.samplespecification')),
            ],
            options={
                'unique_together': {('samplespec', 'datapointtype')},
            },
        ),
        migrations.CreateModel(
            name='SampleDatapoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, default='', max_length=1000, null=True)),
                ('sampledpts', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datapoint_sampledpts', to='ui.sampledpts')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateofreceipt', models.DateField(verbose_name='Date')),
                ('mutation', models.IntegerField(blank=True, null=True)),
                ('type', models.CharField(choices=[('solid', 'Solid'), ('liquid', 'Liquid'), ('na', 'Not Available')], default='na', max_length=8)),
                ('location', models.CharField(default='', max_length=255)),
                ('icd10', models.CharField(default='', max_length=255)),
                ('projectid', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='sample_projectid', to='ui.projectid')),
            ],
            options={
                'unique_together': {('projectid', 'dateofreceipt')},
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('signup_confirmation', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PatientSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, related_name='patientspec_project', to='ui.project')),
            ],
        ),
        migrations.CreateModel(
            name='PatientDPTs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mandatory', models.BooleanField(default=False)),
                ('default', models.CharField(blank=True, max_length=1000, null=True)),
                ('datapointtype', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='patientdpts_datapointtype', to='ui.datapointtype')),
                ('patientspec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patientdpts_patientspec', to='ui.patientspecification')),
            ],
            options={
                'unique_together': {('patientspec', 'datapointtype')},
            },
        ),
        migrations.CreateModel(
            name='PatientDatapoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, default='', max_length=1000, null=True)),
                ('patientdpts', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datapoint_patientdpts', to='ui.patientdpts')),
            ],
        ),
        migrations.AddField(
            model_name='datapointtype',
            name='validators',
            field=models.ManyToManyField(related_name='datapointvalidator_validators', to='ui.DatapointValidator'),
        ),
        migrations.CreateModel(
            name='Datapoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, default='', max_length=1000, null=True)),
                ('specdpts', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datapoint_specdpts', to='ui.specdpts')),
            ],
        ),
        migrations.CreateModel(
            name='ConfDPTs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mandatory', models.BooleanField(default=False)),
                ('default', models.CharField(blank=True, default='', max_length=1000, null=True)),
                ('chipsetspec', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='confdpts_chipsetspec', to='ui.chipsetspecification')),
                ('datapointtype', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='confdpts_datapointtype', to='ui.datapointtype')),
            ],
            options={
                'unique_together': {('chipsetspec', 'datapointtype')},
            },
        ),
        migrations.AddField(
            model_name='chipsetspecification',
            name='genes',
            field=models.ManyToManyField(related_name='chipsetspec_genes', to='ui.Gene'),
        ),
        migrations.AddField(
            model_name='chipsetspecification',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='chipsetspec_project', to='ui.project'),
        ),
        migrations.CreateModel(
            name='ChipsetDatapoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(blank=True, default='', max_length=1000, null=True)),
                ('confdpts', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datapoint_confdpts', to='ui.confdpts')),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='datapoint_gene', to='ui.gene')),
            ],
        ),
        migrations.CreateModel(
            name='GeneAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datapoints', models.ManyToManyField(related_name='geneanalysis_datapoint', to='ui.Datapoint')),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='geneanalysis_sample', to='ui.sample')),
                ('specification', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='geneanalysis_specification', to='ui.specification')),
            ],
            options={
                'unique_together': {('sample', 'specification')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='chipsetspecification',
            unique_together={('name', 'manufacturer', 'version', 'project')},
        ),
        migrations.CreateModel(
            name='ChipsetAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chipsetspec', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='chipsetanalysis_chipsetspec', to='ui.chipsetspecification')),
                ('datapoints', models.ManyToManyField(related_name='chipsetanalysis_datapoint', to='ui.ChipsetDatapoint')),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='chipsetanalysis_sample', to='ui.sample')),
            ],
            options={
                'unique_together': {('sample', 'chipsetspec')},
            },
        ),
    ]
