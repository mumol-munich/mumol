from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.html import format_html
from django.urls import reverse

from .choices import *
from .validators import alnum_us_minus_space_val

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(
        max_length=100, blank=True, null=True)  # remove null
    last_name = models.CharField(
        max_length=100, blank=True, null=True)  # remove null
    is_admin = models.BooleanField(default=False)
    signup_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Project(models.Model):  # admin
    name = models.CharField(max_length=255, unique=True, validators = [alnum_us_minus_space_val])
    users = models.ManyToManyField(
        User, related_name='project_user')

    def __str__(self):
        return self.name

    # def delete(self):
    #     project = Project.objects.filter(project=self)
    #     if project:
    #         if 
    #     super(Project, self).delete()


class AnalysisMethod(models.Model):  # admin
    name = models.CharField(max_length=255, unique=True, validators = [alnum_us_minus_space_val])

    def __str__(self):
        return self.name


class Gene(models.Model):
    name = models.CharField(max_length=255, unique=True) # specify validator

    def __str__(self):
        return self.name

class DatapointValidator(models.Model):  # admin
    validator = models.CharField(choices=DPVALIDATOR, max_length=32)
    value = models.CharField(max_length=255)
    errormessage = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.validator} {self.value} ({self.errormessage})"
# create python file to validate this


class DatapointType(models.Model):  # admin
    name = models.CharField(max_length=255, validators = [alnum_us_minus_space_val], unique = True)
    type = models.CharField(
        choices=DPTYPE, default=DPTYPE.varchar, max_length=32)
    validators = models.ManyToManyField(
        DatapointValidator, related_name='datapointvalidator_validators')
    helptext = models.CharField(
        max_length=255, default='', blank=True, null=True)
    options = models.CharField(
        max_length=255, default='', blank=True, null=True)
    rcmd_methods = models.ManyToManyField(AnalysisMethod, related_name="rcmd_methods", editable=False)

    def __str__(self):
        return f"{self.name} ({self.helptext})"

class Specification(models.Model):  # admin
    project = models.ForeignKey(
        Project, on_delete=models.RESTRICT, related_name="specification_project")
    gene = models.ForeignKey(
        Gene, on_delete=models.RESTRICT, related_name="specification_gene")
    method = models.ForeignKey(
        AnalysisMethod, on_delete=models.RESTRICT, related_name="specification_method")
    # status = models.CharField(
    #     choices=DPSTATUS, default=DPSTATUS.na, max_length=32)
    status = models.CharField(max_length=255, validators = [alnum_us_minus_space_val])
    # depreciated = models.BooleanField(default=False)
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.name = f"{self.project}-{self.gene}-{self.method}-{self.status}"
        super(Specification, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"
    def get_name(self):
        return f'{self.method} > {self.gene} > {self.status}'
    class Meta:
        unique_together = ('project', 'gene', 'method', 'status', )


class SpecDPTs(models.Model):  # admin
    specification = models.ForeignKey(
        Specification, on_delete=models.CASCADE, related_name="specdpts_specification")
    datapointtype = models.ForeignKey(
        DatapointType, on_delete=models.RESTRICT, related_name="specdpts_datapointtype")
    mandatory = models.BooleanField(default=False)
    default = models.CharField(
        max_length=1000, blank=True, null=True)
    def __str__(self):
        htmlstr = f"{self.datapointtype}"
        if self.mandatory:
            htmlstr += f" - Mandatory"
        if self.default:
            htmlstr += f" - Default: {self.default}"
        return htmlstr
    class Meta:
        unique_together = ('specification', 'datapointtype',)

class ChipsetSpecification(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    genes = models.ManyToManyField(
        Gene, related_name='chipsetspec_genes')
    project = models.ForeignKey(
        Project, on_delete=models.RESTRICT, related_name="chipsetspec_project")
    
    class Meta:
        unique_together = ('name', 'manufacturer', 'version', 'project', )

    def __str__(self):
        return f"{self.name} {self.version} {self.manufacturer}"
    def get_name(self):
        return format_html(f'{self.name}&nbsp<span class="grey-text">(version: {self.version}, manufacturer: {self.manufacturer})</span>')
    
class ConfDPTs(models.Model):  # admin
    chipsetspec = models.ForeignKey(ChipsetSpecification, on_delete = models.CASCADE, related_name = 'confdpts_chipsetspec', blank = True, null = True) # remove blank and null
    datapointtype = models.ForeignKey(
        DatapointType, on_delete=models.RESTRICT, related_name="confdpts_datapointtype")
    mandatory = models.BooleanField(default=False)
    default = models.CharField(
        max_length=1000, default='', blank=True, null=True)
    def __str__(self):
        htmlstr = f"{self.datapointtype}"
        if self.mandatory:
            htmlstr += f" - Mandatory"
        return htmlstr
    class Meta:
        unique_together = ('chipsetspec', 'datapointtype',)

# user
class Patient(models.Model):  # user
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    dateofbirth = models.DateField(_("Date of Birth"))

    class Meta:
        unique_together = ['firstname', 'lastname', 'dateofbirth']
    def __str__(self):
        return f"{self.lastname}, {self.firstname} DOB: {self.dateofbirth}"
    def get_dateofbirth(self):
        # return self.dateofbirth.strftime('%Y-%m-%d')
        return self.dateofbirth.strftime('%d.%m.%Y')

class ProjectId(models.Model):  # user
    project = models.ForeignKey(
        Project, on_delete=models.RESTRICT, related_name="projectid_project")
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="projectid_patient")
    projectid = models.CharField(max_length=255) # unique id within project
    class Meta:
        unique_together = (('project', 'projectid',), ('project', 'patient', 'projectid',),)
    def __str__(self):
        return f"{self.projectid} - {self.project}"
    def get_name(self):
        return f'{self.patient.lastname}, {self.patient.firstname}'
    def get_dateofbirth(self):
        return self.patient.get_dateofbirth()

class Sample(models.Model):  # user
    projectid = models.ForeignKey(
        ProjectId, on_delete=models.RESTRICT, related_name="sample_projectid")
    dateofreceipt = models.DateField(_("Date"))
    mutation = models.IntegerField(null=True, blank=True)  # notsure
    type = models.CharField(choices=STYPE, default = STYPE.na, max_length=8)
    location = models.CharField(max_length=255, default = '')
    icd10 = models.CharField(max_length=255, default = '')
    class Meta:
        unique_together = ['projectid', 'dateofreceipt']
    def get_dateofreceipt(self):
        # return self.dateofreceipt.strftime('%Y-%m-%d')
        return self.dateofreceipt.strftime('%d.%m.%Y')

class Datapoint(models.Model): # user
    specdpts = models.ForeignKey(
        SpecDPTs, on_delete=models.RESTRICT, related_name="datapoint_specdpts")
    value = models.TextField(
        max_length=1000, default='', blank=True, null=True)
    def get_datapointtype_id(self):
        return self.specdpts.datapointtype_id

class ChipsetDatapoint(models.Model):
    gene = models.ForeignKey(
        Gene, on_delete=models.RESTRICT, related_name="datapoint_gene")
    confdpts = models.ForeignKey(
        ConfDPTs, on_delete=models.RESTRICT, related_name="datapoint_confdpts")
    value = models.TextField(
        max_length=1000, default='', blank=True, null=True)
    def get_datapointtype_id(self):
        return self.confdpts.datapointtype_id
    
class GeneAnalysis(models.Model): # user
    sample = models.ForeignKey(
        Sample, on_delete=models.RESTRICT, related_name="geneanalysis_sample")
    specification = models.ForeignKey(
        Specification, on_delete=models.RESTRICT, related_name="geneanalysis_specification")
    datapoints =  models.ManyToManyField(
        Datapoint, related_name='geneanalysis_datapoint')

    # deleting in queryset doesnot work properly
    def delete(self, *args, **kwargs):
        self.datapoints.all().delete()
        super(GeneAnalysis, self).delete(*args, **kwargs)
    
    class Meta:
        unique_together = ('sample', 'specification',)

class ChipsetAnalysis(models.Model): # user
    sample = models.ForeignKey(
        Sample, on_delete=models.RESTRICT, related_name="chipsetanalysis_sample")
    chipsetspec = models.ForeignKey(
        ChipsetSpecification, on_delete=models.RESTRICT, related_name="chipsetanalysis_chipsetspec")
    datapoints =  models.ManyToManyField(
        ChipsetDatapoint, related_name='chipsetanalysis_datapoint')

    # deleting in queryset doesnot work properly
    def delete(self, *args, **kwargs):
        self.datapoints.all().delete()
        super(ChipsetAnalysis, self).delete(*args, **kwargs)
    
    class Meta:
        unique_together = ('sample', 'chipsetspec',)


# class GeneAnalysis(models.Model):  # user
#     sample = models.ForeignKey(
#         Sample, on_delete=models.RESTRICT, related_name="geneanalysis_sample")
#     specification = models.ForeignKey(
#         Specification, on_delete=models.RESTRICT, related_name="geneanalysis_specification", blank = True, null = True)
#     specdpts = models.ForeignKey(
#         SpecDPTs, on_delete=models.RESTRICT, related_name="geneanalysis_specdpts")
#     value = models.TextField(
#         max_length=1000, default='', blank=True, null=True)
#     class Meta:
#         unique_together = ['sample', 'specdpts']
#     def save(self, *args, **kwargs):
#         self.specification_id = self.specdpts.specification_id
#         super(GeneAnalysis, self).save(*args, **kwargs)

# class ChipsetAnalysis(models.Model):  # user
#     sample = models.ForeignKey(
#         Sample, on_delete=models.RESTRICT, related_name="chipsetanalysis_sample")
#     chipsetspec = models.ForeignKey(ChipsetSpecification, on_delete = models.CASCADE, related_name = 'chipsetanalysis_chipsetspec', blank = True, null = True) # remove blank and null
#     confdpts = models.ForeignKey(
#         ConfDPTs, on_delete=models.RESTRICT, related_name="chipsetanalysis_confdpts")
#     value = models.TextField(
#         max_length=1000, default='', blank=True, null=True)
#     class Meta:
#         unique_together = ['sample', 'confdpts']
#     def save(self, *args, **kwargs):
#         self.chipsetspec_id = self.confdpts.chipsetspec_id
#         super(ChipsetAnalysis, self).save(*args, **kwargs)

# new
class PatientSpecification(models.Model):  # admin
    project = models.OneToOneField(
        Project, on_delete=models.RESTRICT, related_name="patientspec")

class SampleSpecification(models.Model):  # admin
    project = models.OneToOneField(
        Project, on_delete=models.RESTRICT, related_name="samplespec")

class PatientDPTs(models.Model):  # admin
    patientspec = models.ForeignKey(
        PatientSpecification, on_delete=models.CASCADE, related_name="patientdpts_patientspec")
    datapointtype = models.ForeignKey(
        DatapointType, on_delete=models.RESTRICT, related_name="patientdpts_datapointtype")
    mandatory = models.BooleanField(default=False)
    default = models.CharField(
        max_length=1000, blank=True, null=True)
    def __str__(self):
        htmlstr = f"{self.datapointtype}"
        if self.mandatory:
            htmlstr += f" - Mandatory"
        if self.default:
            htmlstr += f" - Default: {self.default}"
        return htmlstr
    class Meta:
        unique_together = ('patientspec', 'datapointtype',)

class SampleDPTs(models.Model):  # admin
    samplespec = models.ForeignKey(
        SampleSpecification, on_delete=models.CASCADE, related_name="sampledpts_samplespec")
    datapointtype = models.ForeignKey(
        DatapointType, on_delete=models.RESTRICT, related_name="sampledpts_datapointtype")
    mandatory = models.BooleanField(default=False)
    default = models.CharField(
        max_length=1000, blank=True, null=True)
    def __str__(self):
        htmlstr = f"{self.datapointtype}"
        if self.mandatory:
            htmlstr += f" - Mandatory"
        if self.default:
            htmlstr += f" - Default: {self.default}"
        return htmlstr
    class Meta:
        unique_together = ('samplespec', 'datapointtype',)


class PatientDatapoint(models.Model): # user
    patientdpts = models.ForeignKey(
        PatientDPTs, on_delete=models.RESTRICT, related_name="datapoint_patientdpts")
    value = models.TextField(
        max_length=1000, default='', blank=True, null=True)
    def get_datapointtype_id(self):
        return self.patientdpts.datapointtype_id

class SampleDatapoint(models.Model): # user
    sampledpts = models.ForeignKey(
        SampleDPTs, on_delete=models.RESTRICT, related_name="datapoint_sampledpts")
    value = models.TextField(
        max_length=1000, default='', blank=True, null=True)
    def get_datapointtype_id(self):
        return self.sampledpts.datapointtype_id

class PatientInfo(models.Model): # user
    projectid = models.OneToOneField(
        ProjectId, on_delete=models.RESTRICT, related_name="patientinfo")
    patientspec = models.ForeignKey(
        PatientSpecification, on_delete=models.RESTRICT, related_name="patientinfo_patientspec")
    datapoints =  models.ManyToManyField(
        PatientDatapoint, related_name='patientinfo_datapoint')

    # deleting in queryset doesnot work properly
    def delete(self, *args, **kwargs):
        self.datapoints.all().delete()
        super(PatientInfo, self).delete(*args, **kwargs)
    
    class Meta:
        unique_together = ('projectid', 'patientspec',)

class SampleInfo(models.Model): # user
    sample = models.OneToOneField(
        Sample, on_delete=models.RESTRICT, related_name="sampleinfo")
    samplespec = models.ForeignKey(
        SampleSpecification, on_delete=models.RESTRICT, related_name="sampleinfo_patientspec")
    datapoints =  models.ManyToManyField(
        SampleDatapoint, related_name='sampleinfo_datapoint')

    # deleting in queryset doesnot work properly
    def delete(self, *args, **kwargs):
        self.datapoints.all().delete()
        super(SampleInfo, self).delete(*args, **kwargs)
    
    class Meta:
        unique_together = ('sample', 'samplespec',)

# new


from .functions import fn_create_or_get_none_datapointtype


@receiver(post_save, sender=Project)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        patientspec = PatientSpecification.objects.create(project=instance)
        samplespec = SampleSpecification.objects.create(project=instance)
        patientspec.save()
        samplespec.save()
        # create dummy dpts
        datapointtype_pk = fn_create_or_get_none_datapointtype()
        patientdpt = PatientDPTs(patientspec = patientspec, datapointtype_id = datapointtype_pk)
        patientdpt.save()
        sampledpt = SampleDPTs(samplespec = samplespec, datapointtype_id = datapointtype_pk)
        sampledpt.save()
    # instance.patientspec_project.save()