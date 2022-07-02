from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count

import operator
from django.db.models import Q
from functools import reduce

import json

from ..models import Project, Sample, Patient, ProjectId, SampleInfo, SampleDPTs, SampleDatapoint, PatientInfo, SampleInfo, PatientDatapoint, SampleDatapoint, PatientDPTs
from ..forms import SampleAddForm, PatientAddForm, ProjectIdAddForm
from ..functions import fn_checkvalidator, fn_generate_projectid, fn_auth_project_user
from ..config import content


@login_required
def samples_view_user(request, project_pk):
    page_num = request.GET.get('page', 1)
    page_length = request.GET.get('length')
    if not page_length:
        page_length = 5
    if not int(page_length) in [5, 10, 25, 50]:
        page_length = 5
    try:
        # check user
        response = fn_auth_project_user(request.user, project_pk)
        if not response['ok']:
            messages.error(request, response['message'])
            return response['return_page']
        samples = Sample.objects.prefetch_related('projectid').filter(projectid__project_id = project_pk)
        samples = samples.annotate(gcount = Count('geneanalysis_sample', distinct=True), ccount = Count('chipsetanalysis_sample', distinct=True))
        # filter
        filterdict = {}
        for tag in request.GET:
            if tag.startswith('tag.'):
                tagwords = tag.split(".")
                if tagwords[1] == 'sample':
                    # dateofreceipt = request.GET[tag].split(" ")[0].split(".")
                    # samples = samples.filter(reduce(operator.and_, (Q(dateofreceipt__contains = int(dor)) for dor in dateofreceipt)))
                    try:
                        sampledate, samplevisit = request.GET[tag].split("(")
                    except:
                        sampledate = request.GET[tag]
                        samplevisit = None
                    samf = Q()
                    if sampledate:
                        sampledate = sampledate.split(".")
                        samd = reduce(operator.and_, (Q(dateofreceipt__contains = int(dor.strip())) for dor in sampledate))
                        if samd:
                            samf.add(samd, Q.AND)
                    if samplevisit:
                        samplevisit = samplevisit.split(")")[0].strip()
                        if samplevisit:
                            samv = Q(visit = samplevisit)
                            if samv:
                                samf.add(samv, Q.AND)
                    if samf:
                        samples = samples.filter(samf)
                if tagwords[1] == 'projectid':
                    filterdict["projectid__projectid__contains"] = request.GET[tag]
                if tagwords[1] == 'patient':
                    if tagwords[2] == 'dateofbirth':
                        dateofbirth = request.GET[tag].split(".")
                        samples = samples.filter(reduce(operator.and_, (Q(projectid__patient__dateofbirth__contains = int(dob)) for dob in dateofbirth)))
                    else:
                        filterdict[f"projectid__patient__{tagwords[2]}__contains"] = request.GET[tag]
                if tagwords[1] == "patientdpt":
                    filterdict["projectid__patientinfo__patientspec__patientdpts_patientspec__id"] = tagwords[2]
                    filterdict["projectid__patientinfo__datapoints__value__contains"] = request.GET[tag]
                if tagwords[1] == 'count':
                    if tagwords[2] == 'geneanalysis':
                        filterdict["gcount"] = request.GET[tag]
                    if tagwords[2] == 'chipsetanalysis':
                        filterdict["ccount"] = request.GET[tag]
                if tagwords[1] == 'sampledpt':
                    filterdict["sampleinfo__samplespec__sampledpts_samplespec__id"] = tagwords[2]
                    filterdict["sampleinfo__datapoints__value__contains"] = request.GET[tag]
        samples = samples.filter(**filterdict)
        # filter
    except Exception as e:
        messages.error(request, e)
        messages.error(request, 'Error in accessing requested project')
        return HttpResponseRedirect(reverse('projects_view_user'))
    paginator = Paginator(samples, page_length)
    page_obj = paginator.get_page(page_num)
    last_sample = samples.last()
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    try:
        patientdpts = list(projects.get(pk = project_pk).patientspec.patientdpts_patientspec.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
    except:
        patientdpts = []  
    try:
        sampledpts = list(projects.get(pk = project_pk).samplespec.sampledpts_samplespec.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
    except Exception as e:
        sampledpts = []
    formpatient = PatientAddForm()
    formprojectid = ProjectIdAddForm()
    formsample = SampleAddForm()
    return render(request, 'ui_new/user/samples/samples_overview.html', dict(projects = projects, project_pk = project_pk, page_obj = page_obj, patientdpts = json.dumps(patientdpts), sampledpts = json.dumps(sampledpts), formpatient = formpatient, formprojectid = formprojectid, formsample = formsample, current_page = 'samples', current_line = "samples", page_length = page_length, last_sample = last_sample))

@login_required
@require_http_methods(['POST'])
def samples_overview_add_remove(request, project_pk):
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    custom_return_page = request.POST.get('return_page')
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # window.location.pathname
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        # add sample
        firstname, lastname, dateofbirth, projectid_val, dateofreceipt, visit = request.POST.get('firstname'), request.POST.get('lastname'), request.POST.get('dateofbirth'), request.POST.get('projectid'), request.POST.get('dateofreceipt'), request.POST.get('visit')
        patient_new = False
        # return HttpResponse(json.dumps(request.POST))
        # get patient
        try:
            patient = Patient.objects.get(firstname = firstname, lastname = lastname, dateofbirth = dateofbirth)
        except Exception as e:
            # new patient
            try:
                patient = Patient(firstname = firstname, lastname = lastname, dateofbirth = dateofbirth)
                patient.save()
                patient_new = True
            except Exception as e:
                messages.error(request, e)
                messages.error(request, 'Error in registering patient')
                return return_page
        # projectid
        response = fn_generate_projectid(project_pk, projectid_val)
        if not response['ok']:
            if not response['projectid_pk']:
                messages.error(request, response['message'])
                if patient_new:
                    patient.delete()
                return return_page
        projectid_val = response['projectid_val']
        # new projectid
        if patient_new:
            projectid = ProjectId(project_id = project_pk, patient_id = patient.pk, projectid = projectid_val)
            projectid.save()
        else:
            try:
                projectid = ProjectId.objects.get(project_id = project_pk, projectid = projectid_val)
            except Exception as e:
                messages.error(request, e)
                messages.error(request, 'Error in accessing project specific id')
                return return_page
        patientdpts_pks = request.POST.get('custompat_pks')
        if patientdpts_pks:
            patientdpts_pks = patientdpts_pks.split(',')
        else:
            patientdpts_pks = []
        try:
            patientinfo = projectid.patientinfo # for editing (later)
        except:
            patientinfo = PatientInfo(projectid = projectid, patientspec_id = projectid.project.patientspec.pk)
            patientinfo.save()
        # with datapoint
        if patientdpts_pks:
            try:
                patdatapoint_pks = []
                for patientdpts_pk in patientdpts_pks:
                    key = f'custompat_{patientdpts_pk}'
                    patientdpts = PatientDPTs.objects.get(pk = patientdpts_pk, patientspec__project_id = project_pk)
                    ivalue = request.POST.get(key)
                    if patientdpts.datapointtype.type == 'multiple':
                        ivalue = request.POST.getlist(key)
                        ivalue = ','.join(ivalue)
                    if patientdpts.mandatory and not ivalue:
                        messages.error(request, 'Mandatory field is not filled')
                        return return_page
                    if ivalue:
                        # check validators
                        response = fn_checkvalidator(ivalue, patientdpts.datapointtype)
                        if not response['ok']:
                            # patientinfo.delete()
                            # PatientDatapoint.objects.filter(pk__in = patdatapoint_pks).delete()
                            [p.delete() for p in PatientDatapoint.objects.filter(pk__in = patdatapoint_pks)]
                            messages.error(request, response['message'])
                            return return_page
                    datapoint = PatientDatapoint(patientdpts = patientdpts, value = ivalue)
                    datapoint.save()
                    patdatapoint_pks.append(datapoint.pk)
                    patientinfo.datapoints.add(datapoint)
            except Exception as e:
                if patient_new:
                    patientinfo.delete()
                    patient.delete()
                messages.error(request, e)
                messages.error(request, 'Error in adding patient info values')
                return return_page
        # get sample
        try:
            sample = Sample.objects.get(projectid_id = projectid.pk, dateofreceipt = dateofreceipt, visit = visit)
            messages.error(request, message = f'Sample already exist with visit {sample.visit}.')
            return return_page
        except Exception as e:
            # new sample
            sample = Sample(projectid_id = projectid.pk, dateofreceipt = dateofreceipt, visit = visit)
            sample.save()
            sample_new = True
        # sampledpts
        sampledpts_pks = request.POST.get('customsam_pks')
        if sampledpts_pks:
            sampledpts_pks = sampledpts_pks.split(',')
        else:
            sampledpts_pks = []
        try:
            sampleinfo = sample.sampleinfo # for editing (later)
        except:
            sampleinfo = SampleInfo(sample = sample, samplespec_id = projectid.project.samplespec.pk)
            sampleinfo.save()
        # with datapoint
        if sampledpts_pks:
            try:
                samdatapoint_pks = []
                for sampledpts_pk in sampledpts_pks:
                    key = f'customsam_{sampledpts_pk}'
                    sampledpts = SampleDPTs.objects.get(pk = sampledpts_pk, samplespec__project_id = project_pk)
                    ivalue = request.POST.get(key)
                    if sampledpts.datapointtype.type == 'multiple':
                        ivalue = request.POST.getlist(key)
                        ivalue = ','.join(ivalue)
                    if sampledpts.mandatory and not ivalue:
                        messages.error(request, 'Mandatory field is not filled')
                        return return_page
                    if ivalue:
                        # check validators
                        response = fn_checkvalidator(ivalue, sampledpts.datapointtype)
                        if not response['ok']:
                            # SampleDatapoint.objects.filter(pk__in = samdatapoint_pks).delete()
                            [s.delete() for s in SampleDatapoint.objects.filter(pk__in = samdatapoint_pks)]
                            if sample_new:
                                sampleinfo.delete()
                                sample.delete()
                            if patient_new:
                                patientinfo.delete()
                                patient.delete()
                            messages.error(request, response['message'])
                            return return_page
                    datapoint = SampleDatapoint(sampledpts = sampledpts, value = ivalue)
                    datapoint.save()
                    samdatapoint_pks.append(datapoint.pk)
                    sampleinfo.datapoints.add(datapoint)
            except Exception as e:
                if sample_new:
                    sampleinfo.delete()
                    sample.delete()
                if patient_new:
                    patientinfo.delete()
                    patient.delete()
                messages.error(request, e)
                messages.error(request, 'Error in adding sample inf values')
                return return_page
        if custom_return_page == 'analysis_genes_add_remove':
            genespec_pk = request.GET.get('genespec')
            if genespec_pk:
                return_page = HttpResponseRedirect(str(reverse(custom_return_page, kwargs = dict(sample_pk = sample.pk)) + '?return=samples_overview' + '&genespec=' + genespec_pk))
            else:
                return_page = HttpResponseRedirect(str(reverse(custom_return_page, kwargs = dict(sample_pk = sample.pk)) + '?return=samples_overview'))
        elif custom_return_page == 'analysis_chipsets_add_remove':
            chipsetspec_pk = request.GET.get('chipsetspec')
            if chipsetspec_pk:
                return_page = HttpResponseRedirect(str(reverse(custom_return_page, kwargs = dict(sample_pk = sample.pk)) + '?return=samples_overview' + '&chipsetspec=' + chipsetspec_pk))
            else:
                return_page = HttpResponseRedirect(str(reverse(custom_return_page, kwargs = dict(sample_pk = sample.pk)) + '?return=samples_overview'))
        messages.success(request, 'Success') 
    # elif access_type == 'remove':
    #     # check user???
    #     sample_pks = request.POST.get('sample_pks').split(',')
    #     try:
    #         [sample.delete() for sample in Sample.objects.filter(pk__in = sample_pks)]
    #         messages.success(request, 'Success')
    #     except Exception as e:
    #         messages.error(request, e)
    #         messages.error(request, 'Error in deleting selected samples')
    return return_page

@login_required
@require_http_methods(['POST'])
def samples_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # window.location.pathname
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        projectid_pk, dateofreceipt, visit = request.POST.get('projectid_pk'), request.POST.get('dateofreceipt'), request.POST.get('visit')
        # return HttpResponse(json.dumps(request.POST))
        try:
            project = Project.objects.get(projectid_project__pk = projectid_pk)
            project_pk = project.pk
            # check user
            response = fn_auth_project_user(request.user, project_pk)
            if not response['ok']:
                messages.error(request, response['message'])
                return response['return_page']
            # get sample
            try:
                sample = Sample.objects.get(projectid_id = projectid_pk, dateofreceipt = dateofreceipt, visit = visit)
                messages.error(request, message = f'Sample already exist with visit {sample.visit}.')
                return return_page
            except Exception as e:
                # new sample
                sample = Sample(projectid_id = projectid_pk, dateofreceipt = dateofreceipt, visit = visit)
                sample.save()
                sample_new = True
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in creating new sample')
        # sampledpts
        sampledpts_pks = request.POST.get('customsam_pks')
        if sampledpts_pks:
            sampledpts_pks = sampledpts_pks.split(',')
        else:
            sampledpts_pks = []
        try:
            sampleinfo = sample.sampleinfo # for editing (later)
        except:
            sampleinfo = SampleInfo(sample = sample, samplespec_id = project.samplespec.pk)
            sampleinfo.save()
        # with datapoint
        if sampledpts_pks:
            try:
                datapoint_pks = []
                for sampledpts_pk in sampledpts_pks:
                    key = f'customsam_{sampledpts_pk}'
                    sampledpts = SampleDPTs.objects.get(pk = sampledpts_pk, samplespec__project_id = project_pk)
                    ivalue = request.POST.get(key)
                    if sampledpts.datapointtype.type == 'multiple':
                        ivalue = request.POST.getlist(key)
                        ivalue = ','.join(ivalue)
                    if sampledpts.mandatory and not ivalue:
                        messages.error(request, 'Mandatory field is not filled')
                        return return_page
                    if ivalue:
                        # check validators
                        response = fn_checkvalidator(ivalue, sampledpts.datapointtype)
                        if not response['ok']:
                            # SampleDatapoint.objects.filter(pk__in = datapoint_pks).delete()
                            [s.delete() for s in SampleDatapoint.objects.filter(pk__in = datapoint_pks)]
                            if sample_new:
                                sampleinfo.delete()
                                sample.delete()
                            messages.error(request, response['message'])
                            return return_page
                    datapoint = SampleDatapoint(sampledpts = sampledpts, value = ivalue)
                    datapoint.save()
                    datapoint_pks.append(datapoint.pk)
                    sampleinfo.datapoints.add(datapoint)
            except Exception as e:
                if sample_new:
                    sampleinfo.delete()
                    sample.delete()
                messages.error(request, e)
                messages.error(request, 'Error in adding sample inf values')
                return return_page
        messages.success(request, 'Success')
    elif access_type == 'remove':
        # check user???
        sample_pks = request.POST.get('sample_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            # [sample.delete() for sample in Sample.objects.filter(pk__in = sample_pks)]
            samples = Sample.objects.filter(pk__in = sample_pks)
            # force_delete
            if force_delete:
                for sample in samples:
                    sample.geneanalysis_sample.all().delete()
                    sample.chipsetanalysis_sample.all().delete()
            [s.delete() for s in samples]
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'Error in deleting selected samples')
    return return_page

@login_required
def sample_view_user(request, sample_pk):
    return_page = HttpResponseRedirect(reverse('projects_view_user'))
    try:
        sample = Sample.objects.prefetch_related('projectid').get(pk = sample_pk)
        project_pk = sample.projectid.project_id
        # check user
        response = fn_auth_project_user(request.user, project_pk)
        if not response['ok']:
            messages.error(request, response['message'])
            return response['return_page']
    except Exception as e:
        messages.error(request, e)
        messages.error(request, 'Error in accessing requested sample')
        return return_page
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    geneanalysis = sample.geneanalysis_sample.values('pk')
    return render(request, 'ui_new/user/samples/sample.html', dict(project_pk = project_pk, projects = projects, sample = sample, projectid = sample.projectid, geneanalysis = geneanalysis, patient_edit_deny = True, current_page = 'sample', current_line = "patients"))
