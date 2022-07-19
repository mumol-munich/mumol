from warnings import filters
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

import operator
from django.db.models import Q
from functools import reduce
import pandas as pd

from ..models import ChipsetAnalysis, DatapointsRow, PatientDPTs, SampleDPTs, Project, User, GeneAnalysis, DatapointType
from ..decorators import admin_required
from ..forms import ProjectAddForm
from ..functions import fn_convert_genespec_json, fn_auth_project_user, fn_geneanalysis_query_df

import json
from datetime import datetime

import csv
from django.http import StreamingHttpResponse

from django.db.models.aggregates import Aggregate
from django.db.models import CharField, Value

from django.db import connection


class GroupConcat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s %(expressions)s)'
    allow_distinct = True
    def __init__(self, expression, delimiter="§", **extra):
        if delimiter is not None:
            self.allow_distinct = False
            delimiter_expr = Value(str(delimiter))
            super().__init__(expression, delimiter_expr, **extra)        
        else:
            super().__init__(expression, **extra)        
    def as_sqlite(self, compiler, connection, **extra_context):
        return super().as_sql(
            compiler, connection,
            function=self.function,
            template=self.template,
            **extra_context
        ) 

class Echo:
    def write(self, value):
        return value


# user
@login_required
def projects_view_user2(request):
    project_redirect = request.GET.get('project_redirect')
    analysis_type = request.GET.get('type')
    page_num = request.GET.get('page', 1)
    page_length = request.GET.get('length')
    if not page_length:
        page_length = 5
    if not int(page_length) in [5, 10, 25, 50]:
        page_length = 5
    if request.user.project_user.exists():
        first_project_id = request.user.project_user.first().pk
    else:
        first_project_id = False
        project_redirect = False
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
        # patientdpts = PatientDPTs.objects.all()
        # sampledpts = SampleDPTs.objects.all()
    else:
        projects = request.user.project_user.order_by('-pk')
        # patientdpts = PatientDPTs.objects.filter(patientspec__project__users = request.user).all()
        # sampledpts = SampleDPTs.objects.filter(samplespec__project__users = request.user).all()
    # new
    patientdpts = PatientDPTs.objects.none()
    sampledpts = SampleDPTs.objects.none()
    for project in projects:
        patientdpts |= project.patientspec.patientdpts_patientspec.all()
        sampledpts |= project.samplespec.sampledpts_samplespec.all()
    # new
    geneanalyses = GeneAnalysis.objects.none()
    chipsetanalyses = ChipsetAnalysis.objects.none()
    if not analysis_type or analysis_type != 'chipset':
        analysis_type = 'gene'
        geneanalyses = GeneAnalysis.objects.filter(sample__projectid__project_id__in = list(projects.values_list('id', flat = True)))
        # filter
        filterdict = {}
        for tag in request.GET:
            if tag.startswith('tag.'):
                tagwords = tag.split(".")
                if tagwords[1] == 'project':
                    filterdict["specification__project__name__contains"] = request.GET[tag]
                if tagwords[1] == 'projectid':
                    filterdict["sample__projectid__projectid__contains"] = request.GET[tag]
                if tagwords[1] == 'patient':
                    if tagwords[2] == "dateofbirth":
                        # dateofbirth = datetime.strptime(request.GET[tag], '%d.%m.%Y')
                        # filterdict[f"sample__projectid__patient__{tagwords[2]}"] = dateofbirth
                        dateofbirth = request.GET[tag].split(".")
                        geneanalyses = geneanalyses.filter(reduce(operator.and_, (Q(sample__projectid__patient__dateofbirth__contains = int(dob)) for dob in dateofbirth)))
                    else:
                        filterdict[f"sample__projectid__patient__{tagwords[2]}__contains"] = request.GET[tag]
                if tagwords[1] == 'patientdpt':
                    filterdict["sample__projectid__patientinfo__patientspec__patientdpts_patientspec__id"] = tagwords[2]
                    filterdict["sample__projectid__patientinfo__datapoints__value__contains"] = request.GET[tag]
                if tagwords[1] == 'geneanalysis':
                    # dateofreceipt = request.GET[tag].split(" ")[0].split(".")
                    # geneanalyses = geneanalyses.filter(reduce(operator.and_, (Q(sample__dateofreceipt__contains = int(dor)) for dor in dateofreceipt)))
                    try:
                        sampledate, samplevisit = request.GET[tag].split("(")
                    except:
                        sampledate = request.GET[tag]
                        samplevisit = None
                    samf = Q()
                    if sampledate:
                        sampledate = sampledate.split(".")
                        samd = reduce(operator.and_, (Q(sample__dateofreceipt__contains = int(dor.strip())) for dor in sampledate))
                        if samd:
                            samf.add(samd, Q.AND)
                    if samplevisit:
                        samplevisit = samplevisit.split(")")[0].strip()
                        if samplevisit:
                            samv = Q(sample__visit = samplevisit)
                            if samv:
                                samf.add(samv, Q.AND)
                    if samf:
                        geneanalyses = geneanalyses.filter(samf)
                if tagwords[1] == 'sampledpt':
                    filterdict["sample__sampleinfo__samplespec__sampledpts_samplespec__id"] = tagwords[2]
                    filterdict["sample__sampleinfo__datapoints__value__contains"] = request.GET[tag]
                if tagwords[1] == 'specification':
                    if tagwords[2] == 'status':
                        filterdict[f"specification__{tagwords[2]}__contains"] = request.GET[tag]
                    else:
                        filterdict[f"specification__{tagwords[2]}__name__contains"] = request.GET[tag]
                if tagwords[1] == 'datapointtype':
                    filterdict[f"datapoints__specdpts__datapointtype_id"] = tagwords[2]
                    filterdict[f"datapoints__value__contains"] = request.GET[tag]
        geneanalyses = geneanalyses.filter(**filterdict)
        # filter
        paginatorobj = geneanalyses
    else:
        chipsetanalyses = ChipsetAnalysis.objects.filter(sample__projectid__project_id__in = list(projects.values_list('id', flat = True)))
        # filter
        filterdict = {}
        for tag in request.GET:
            if tag.startswith('tag.'):
                tagwords = tag.split(".")
                if tagwords[1] == 'project':
                    filterdict["chipsetspec__project__name__contains"] = request.GET[tag]
                if tagwords[1] == 'projectid':
                    filterdict["sample__projectid__projectid__contains"] = request.GET[tag]
                if tagwords[1] == 'patient':
                    if tagwords[2] == "dateofbirth":
                        dateofbirth = request.GET[tag].split(".")
                        chipsetanalyses = chipsetanalyses.filter(reduce(operator.and_, (Q(sample__projectid__patient__dateofbirth__contains = int(dob)) for dob in dateofbirth)))
                    else:
                        filterdict[f"sample__projectid__patient__{tagwords[2]}__contains"] = request.GET[tag]
                if tagwords[1] == 'patientdpt':
                    filterdict["sample__projectid__patientinfo__patientspec__patientdpts_patientspec__id"] = tagwords[2]
                    filterdict["sample__projectid__patientinfo__datapoints__value__contains"] = request.GET[tag]
                if tagwords[1] == 'chipsetanalysis':
                    try:
                        sampledate, samplevisit = request.GET[tag].split("(")
                    except:
                        sampledate = request.GET[tag]
                        samplevisit = None
                    samf = Q()
                    if sampledate:
                        sampledate = sampledate.split(".")
                        samd = reduce(operator.and_, (Q(sample__dateofreceipt__contains = int(dor.strip())) for dor in sampledate))
                        if samd:
                            samf.add(samd, Q.AND)
                    if samplevisit:
                        samplevisit = samplevisit.split(")")[0].strip()
                        if samplevisit:
                            samv = Q(sample__visit = samplevisit)
                            if samv:
                                samf.add(samv, Q.AND)
                    if samf:
                        chipsetanalyses = chipsetanalyses.filter(samf)
                if tagwords[1] == 'sampledpt':
                    filterdict["sample__sampleinfo__samplespec__sampledpts_samplespec__id"] = tagwords[2]
                    filterdict["sample__sampleinfo__datapoints__value__contains"] = request.GET[tag]
                if tagwords[1] == 'specification':
                    if tagwords[2] == 'name':
                        try:
                            chipname, chipinfo = request.GET[tag].split("(")
                            chipinfo = chipinfo.strip().split(",")
                        except:
                            chipname = request.GET[tag].strip()
                            chipinfo = None
                        chipf = Q()
                        if chipname:
                            chipn = Q(chipsetspec__name__contains = chipname)
                            if chipn:
                                chipf.add(chipn, Q.AND)
                        if chipinfo:
                            chipinfo = [c.replace('version:', '').replace('manufacturer:', '').split(")")[0].strip() for c in chipinfo]
                            print(chipinfo)
                            chipv = reduce(operator.or_, (Q(chipsetspec__version = v) for v in chipinfo))
                            chipf2 = Q()
                            if chipv:
                                chipf2.add(chipv, Q.OR)
                            chipm = reduce(operator.or_, (Q(chipsetspec__manufacturer__contains = m) for m in chipinfo))
                            if chipm:
                                chipf2.add(chipm, Q.OR)
                            if chipf2:
                                chipf.add(chipf2, Q.AND)
                        if chipf:
                            chipsetanalyses = chipsetanalyses.filter(chipf)
                    if tagwords[2] == 'genes':
                        # filterdict["chipsetspec__genes__name__contains"] = request.GET[tag]
                        messages.error(request, 'This functionality is not available for Genes')
                        return HttpResponseRedirect(reverse('projects_view_user') + '?project_redirect=false&type=chipset&length=' + page_length)
                if tagwords[1] == 'datapointtype':
                    # filterdict[f"datapoints__confdpts__datapointtype_id"] = tagwords[2]
                    # filterdict[f"datapoints__value__contains"] = request.GET[tag]
                    messages.error(request, 'This functionality is not available for Chipset datapoints')
                    return HttpResponseRedirect(reverse('projects_view_user') + '?project_redirect=false&type=chipset&length=' + page_length)
        chipsetanalyses = chipsetanalyses.filter(**filterdict)
        # filter
        paginatorobj = chipsetanalyses
    paginator = Paginator(paginatorobj, page_length)
    page_obj = paginator.get_page(page_num)
    datapointtypes = DatapointType.objects.values('pk', 'name')
    # if analysis_type == 'chipset':
    #     return render(request, 'ui_new/user/projects/projects_tmpchipset.html', dict(projects = projects, analysis_type = analysis_type, datapointtypes = datapointtypes, project_link_deny = True, project_redirect = project_redirect, first_project_id = first_project_id, patientdpts = patientdpts, sampledpts = sampledpts, page_obj = page_obj, page_length = page_length))
    return render(request, 'ui_new/user/projects/projects.html', dict(projects = projects, analysis_type = analysis_type, datapointtypes = datapointtypes, project_link_deny = True, project_redirect = project_redirect, first_project_id = first_project_id, patientdpts = patientdpts, sampledpts = sampledpts, page_obj = page_obj, page_length = page_length))

@login_required
def projects_view_user(request):
    project_redirect = request.GET.get('project_redirect')
    analysis_type = request.GET.get('type')
    page_num = request.GET.get('page', 1)
    page_length = request.GET.get('length', 5)
    try:
        page_length = int(page_length)
    except:
        page_length = 5
    if not page_length in [5, 10, 25, 50]:
        page_length = 5
    if request.user.project_user.exists():
        first_project_id = request.user.project_user.first().pk
    else:
        first_project_id = False
        project_redirect = False
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    patientdpts = PatientDPTs.objects.none()
    sampledpts = SampleDPTs.objects.none()
    for project in projects:
        patientdpts |= project.patientspec.patientdpts_patientspec.all()
        sampledpts |= project.samplespec.sampledpts_samplespec.all()
    datapointtypes = DatapointType.objects.values('pk', 'name')
    if not analysis_type or analysis_type != 'chipset':
        datapointsrows = DatapointsRow.objects.filter(geneanalysis_datapointsrows__sample__projectid__project_id__in = list(projects.values_list('id', flat = True)))
        # filter
        filterdict = {}
        for tag in request.GET:
            if tag.startswith('tag.'):
                tagwords = tag.split(".")
                if tagwords[1] == 'project':
                    filterdict["geneanalysis_datapointsrows__specification__project__name__contains"] = request.GET[tag]
                if tagwords[1] == 'projectid':
                    filterdict["geneanalysis_datapointsrows__sample__projectid__projectid__contains"] = request.GET[tag]
                if tagwords[1] == 'patient':
                    if tagwords[2] == "dateofbirth":
                        dateofbirth = request.GET[tag].split(".")
                        datapointsrows = datapointsrows.filter(reduce(operator.and_, (Q(geneanalysis_datapointsrows__sample__projectid__patient__dateofbirth__contains = int(dob)) for dob in dateofbirth)))
                    else:
                        filterdict[f"geneanalysis_datapointsrows__sample__projectid__patient__{tagwords[2]}__contains"] = request.GET[tag]
                if tagwords[1] == 'patientdpt':
                    filterdict["geneanalysis_datapointsrows__sample__projectid__patientinfo__patientspec__patientdpts_patientspec__id"] = tagwords[2]
                    filterdict["geneanalysis_datapointsrows__sample__projectid__patientinfo__datapoints__value__contains"] = request.GET[tag]
                if tagwords[1] == 'geneanalysis':
                    try:
                        sampledate, samplevisit = request.GET[tag].split("(")
                    except:
                        sampledate = request.GET[tag]
                        samplevisit = None
                    samf = Q()
                    if sampledate:
                        sampledate = sampledate.split(".")
                        samd = reduce(operator.and_, (Q(geneanalysis_datapointsrows__sample__dateofreceipt__contains = int(dor.strip())) for dor in sampledate))
                        if samd:
                            samf.add(samd, Q.AND)
                    if samplevisit:
                        samplevisit = samplevisit.split(")")[0].strip()
                        if samplevisit:
                            samv = Q(geneanalysis_datapointsrows__sample__visit = samplevisit)
                            if samv:
                                samf.add(samv, Q.AND)
                    if samf:
                        datapointsrows = datapointsrows.filter(samf)
                if tagwords[1] == 'sampledpt':
                    filterdict["geneanalysis_datapointsrows__sample__sampleinfo__samplespec__sampledpts_samplespec__id"] = tagwords[2]
                    filterdict["geneanalysis_datapointsrows__sample__sampleinfo__datapoints__value__contains"] = request.GET[tag]
                if tagwords[1] == 'specification':
                    if tagwords[2] == 'status':
                        filterdict[f"geneanalysis_datapointsrows__specification__{tagwords[2]}__contains"] = request.GET[tag]
                    else:
                        filterdict[f"geneanalysis_datapointsrows__specification__{tagwords[2]}__name__contains"] = request.GET[tag]
                if tagwords[1] == 'datapointtype':
                    filterdict[f"datapoints__specdpts__datapointtype_id"] = tagwords[2]
                    filterdict[f"datapoints__value__contains"] = request.GET[tag]
        datapointsrows = datapointsrows.filter(**filterdict)
        # filter
        paginatorobj = datapointsrows
    else:
        pass
    paginator = Paginator(paginatorobj, page_length)
    page_obj = paginator.get_page(page_num)
    return render(request, 'ui_new/user/projects/projects_new.html', dict(analysis_type = analysis_type, datapointtypes = datapointtypes, patientdpts = patientdpts, sampledpts = sampledpts, page_obj = page_obj, project_redirect = project_redirect, first_project_id = first_project_id, page_length = page_length))


# new
@login_required
def queries_gene_user(request):
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    conn = connection.cursor()
    conn.execute('''
select projectQuery.projectName, 
patientQuery.projectid, patientQuery.firstname, patientQuery.lastname, patientQuery.dateofbirth, patientQuery.patientDatapointType, patientQuery.patientDatapoint, 
sampleQuery.dateofreceipt, sampleQuery.visit, sampleQuery.sampleDatapointType, sampleQuery.sampleDatapoint,
rowQuery.method, rowQuery.gene, rowQuery.result, rowQuery.datapointType, rowQuery.datapoint,
rowQuery.datapointsrow_id from (
    select distinct ui_project.id as project_id, ui_project.name as projectName
    from ui_project
    left join ui_project_users on ui_project_users.project_id = ui_project.id
    left join auth_user on auth_user.id = ui_project_users.user_id
    left join ui_profile on ui_profile.user_id = auth_user.id ''' + ('' if request.user.profile.is_admin else 'where auth_user.username = "' + request.user.username + '"') + '''
) projectQuery left join (
    select ui_projectid.project_id, ui_projectid.id as projectid_id, ui_projectid.projectid, ui_patient.firstname, ui_patient.lastname, ui_patient.dateofbirth,
    group_concat(ui_datapointtype.name, '|') as patientDatapointType,
    group_concat(ui_patientdatapoint.value, '|') as patientDatapoint
    from ui_projectid
    left join ui_patient on ui_patient.id = ui_projectid.patient_id
    left join ui_patientinfo on ui_patientinfo.projectid_id = ui_projectid.id
    left join ui_patientinfo_datapoints on ui_patientinfo_datapoints.patientinfo_id = ui_patientinfo.id
    left join ui_patientdatapoint on ui_patientdatapoint.id = ui_patientinfo_datapoints.patientdatapoint_id
    left join ui_patientdpts on ui_patientdpts.id = ui_patientdatapoint.patientdpts_id 
    left join ui_datapointtype on ui_datapointtype.id = ui_patientdpts.datapointtype_id
    group by ui_projectid.id
) patientQuery on patientQuery.project_id = projectQuery.project_id left join (
    select ui_sample.id as sample_id, ui_sample.projectid_id, ui_sample.dateofreceipt, ui_sample.visit,
    group_concat(ui_datapointtype.name, '|') as sampleDatapointType,
    group_concat(ui_sampledatapoint.value, '|') as sampleDatapoint
    from ui_sample
    left join ui_sampleinfo on ui_sampleinfo.sample_id = ui_sample.id
    left join ui_sampleinfo_datapoints on ui_sampleinfo_datapoints.sampleinfo_id = ui_sampleinfo.id
    left join ui_sampledatapoint on ui_sampledatapoint.id = ui_sampleinfo_datapoints.sampledatapoint_id
    left join ui_sampledpts on ui_sampledpts.id = ui_sampledatapoint.sampledpts_id
    left join ui_datapointtype on ui_datapointtype.id = ui_sampledpts.datapointtype_id
    group by ui_sample.id
) sampleQuery on sampleQuery.projectid_id = patientQuery.projectid_id inner join (
    select ui_datapointsrow.id as datapointsrow_id, ui_geneanalysis.sample_id as sample_id,
    ui_analysismethod.name as method,
    ui_gene.name as gene,
    ui_specification.status as result,
    group_concat(ui_datapointtype.name, '|') as datapointType,
    group_concat(ui_datapoint.value, '|') as datapoint
    from ui_datapointsrow
    left join ui_geneanalysis_datapointsrows on ui_geneanalysis_datapointsrows.datapointsrow_id = ui_datapointsrow.id
    left join ui_geneanalysis on ui_geneanalysis.id = ui_geneanalysis_datapointsrows.geneanalysis_id
    left join ui_specification on ui_specification.id = ui_geneanalysis.specification_id
    left join ui_analysismethod on ui_analysismethod.id = ui_specification.method_id
    left join ui_gene on ui_gene.id = ui_specification.gene_id
    left join ui_datapointsrow_datapoints on ui_datapointsrow_datapoints.datapointsrow_id = ui_datapointsrow.id
    left join ui_datapoint on ui_datapoint.id = ui_datapointsrow_datapoints.datapoint_id
    left join ui_specdpts on ui_specdpts.id = ui_datapoint.specdpts_id
    left join ui_datapointtype on ui_datapointtype.id = ui_specdpts.datapointtype_id
    group by ui_datapointsrow.id
) rowQuery on rowQuery.sample_id = sampleQuery.sample_id
    ''')
    df = pd.DataFrame(conn.fetchall())
    df.columns = [c[0] for c in conn.description]
    response = fn_geneanalysis_query_df(df)
    if not response['ok']:
        messages.error(request, response['message'])
        return HttpResponseRedirect(reverse('projects_view_user'))
    df = response['df']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=gene_analysis_all.tsv'
    df.to_csv(path_or_buf = response, sep = '\t', index = False)
    return response
    # pseudo_buffer = Echo()
    # writer = csv.writer(pseudo_buffer, delimiter="\t")
    # return StreamingHttpResponse(
    # # return HttpResponse(
    #     # (writer.writerow(dat1[i] + dat2[i] + dat3[i] + dat4[i]) for i in range(dat1.count())),
    #     (writer.writerow(dat1) for dat1 in conn.fetchall()),
    #     content_type="text/csv",
    #     headers={'Content-Disposition': 'attachment; filename="1.tsv"'},
    # )
    # return HttpResponse('ok')
# new

@login_required
def project_view_user(request, project_pk):
    try:
        # check user
        response = fn_auth_project_user(request.user, project_pk)
        if not response['ok']:
            messages.error(request, response['message'])
            return response['return_page']
        project = Project.objects.get(pk = project_pk)
    except Exception as e:
        messages.error(request, e)
        messages.error(request, 'Error in accessing requested project')
        return HttpResponseRedirect(reverse('projects_view_user'))
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    return render(request, 'ui_new/user/projects/project.html', dict(projects = projects, project = project, project_pk = project.pk, current_page = 'project'))



# admin
@login_required
@admin_required
def projects_view(request):
    projects = Project.objects.order_by('-pk')
    formadd = ProjectAddForm()
    return render(request, 'ui_new/admin/projects/projects.html', dict(projects=projects, formproject=formadd, project_add_allow = True))

@login_required
@admin_required
@require_http_methods(['POST'])
def projects_add_remove(request):
    return_page = HttpResponseRedirect(
        reverse('projects_view'))
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        form = ProjectAddForm(request.POST or None)
        if form.is_valid():
            project = form.save()
            messages.success(request, 'Success')
            return HttpResponseRedirect(reverse('project_view', kwargs = dict(project_pk = project.pk)))
        else:
            messages.error(request, form.errors)
    elif access_type == 'remove':
        project_pks = request.POST.get('project_pks').split(',')
        try:
            projects = Project.objects.filter(pk__in=project_pks)
            # projects.delete()
            [p.delete() for p in projects]
            messages.success(request, 'Success')
        except Exception as e:
            messages.error(request, e)
    return return_page

@login_required
@admin_required
@require_http_methods(['POST'])
def project_users_add_remove(request, project_pk):
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    return_page = HttpResponseRedirect(reverse('project_view', kwargs = dict(project_pk = project_pk)))
    access_type = request.POST.get('access_type')
    try:
        project = Project.objects.get(pk = project_pk)
    except:
        messages.error(request, 'Error in accessing requested project')
        return HttpResponseRedirect(reverse('projects_view'))
    if access_type == 'add':
        user_pks = request.POST.getlist('custom_add_users')
        if not user_pks:
            messages.error(request, 'Please select at least one user to add')
        else:
            for user_pk in user_pks:
                project.users.add(user_pk)
            messages.success(request, f'{len(user_pks)} user(s) added to the project successfully')
    elif access_type == 'remove':
        user_pks = request.POST.getlist('custom_remove_users')
        if not user_pks:
            messages.error(request, 'Please select at least one user to remove')
        else:
            for user_pk in user_pks:
                project.users.remove(user_pk)
            messages.success(request, f'{len(user_pks)} user(s) removed from the project successfully')
    return return_page

@login_required
@admin_required
def project_view(request, project_pk):
    try:
        project = Project.objects.get(pk = project_pk)
    except:
        messages.error(request, 'Error in accessing requested project')
        return HttpResponseRedirect(reverse('projects_view'))
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    otherusers = User.objects.exclude(pk__in = project.users.all())
    projects = Project.objects.order_by('-pk')
    formadd = ProjectAddForm()
    # convert genespecs to required nested json
    genespecs = list(project.specification_project.order_by('method__name', 'gene__name', 'status').values('pk', 'method_id', 'method__name', 'gene_id', 'gene__name', 'status'))
    chipsetspecs = project.chipsetspec_project.all()
    response = fn_convert_genespec_json(genespecs)
    if not response['ok']:
        messages.error(request, 'Error in fetching genespecs json')
    else:
        genespecs = response['genespecs']
    return render(request, 'ui_new/admin/projects/project.html', dict(projects=projects, otherusers = otherusers, formproject=formadd, project = project, genespecs = genespecs, chipsetspecs = chipsetspecs, project_link_allow = True, project_add_allow = True))
