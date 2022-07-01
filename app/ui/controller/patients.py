from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

import uuid, json

import operator
from django.db.models import Q
from functools import reduce

from ..models import Patient, PatientDPTs, Project, ProjectId, PatientInfo, PatientDatapoint
from ..forms import SampleAddForm, PatientAddForm, ProjectIdAddForm
from ..functions import fn_checkvalidator, fn_auth_project_user, fn_create_or_get_none_datapointtype, fn_generate_projectid
from ..config import content


@login_required
def patients_view_user(request, project_pk):
    page_num = request.GET.get('page', 1)
    page_length = request.GET.get('length')
    if not page_length:
        page_length = 5
    if not int(page_length) in [5, 10, 25, 50]:
        page_length = 5
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    # patients = Patient.objects.order_by('-pk')
    # patients = Patient.objects.filter(projectid_patient__project_id = project_pk).order_by('pk')
    projectids = ProjectId.objects.filter(project_id = project_pk)
    last_projectid = projectids.last()
    # filter
    filterdict = {}
    for tag in request.GET:
        if tag.startswith('tag.'):
            tagwords = tag.split(".")
            if tagwords[1] == 'projectid':
                if tagwords[2] == 'projectid':
                    filterdict["projectid__contains"] = request.GET[tag]
                if tagwords[2] == 'otherids':
                    messages.error(request, 'Filtering based on otherids are not available')
                    return HttpResponseRedirect(reverse('patients_view_user', kwargs=dict(project_pk = project_pk)))
            if tagwords[1] == 'patient':
                if tagwords[2] == "dateofbirth":
                    dateofbirth = request.GET[tag].split(".")
                    projectids = projectids.filter(reduce(operator.and_, (Q(patient__dateofbirth__contains = int(dob)) for dob in dateofbirth)))
                else:
                    filterdict[f"patient__{tagwords[2]}__contains"] = request.GET[tag]
            if tagwords[1] == 'patientdpt':
                filterdict["patientinfo__patientspec__patientdpts_patientspec__id"] = tagwords[2]
                filterdict["patientinfo__datapoints__value__contains"] = request.GET[tag]
    projectids = projectids.filter(**filterdict)
    # filter
    paginator = Paginator(projectids, page_length)
    page_obj = paginator.get_page(page_num)
    try:
        patientdpts = list(projects.get(pk = project_pk).patientspec.patientdpts_patientspec.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
    except:
        patientdpts = []
    formpatient = PatientAddForm()
    formprojectid = ProjectIdAddForm()
    return render(request, 'ui_new/user/patients/patients.html', dict(project_pk = project_pk, patientdpts = json.dumps(patientdpts), projects = projects, page_obj = page_obj, formpatient = formpatient, formprojectid = formprojectid, current_page = 'patients', current_line = "patients", page_length = page_length, last_projectid = last_projectid))

@login_required
@require_http_methods(['POST'])
def patients_add_remove(request, project_pk):
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # window.location.pathname
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        firstname, lastname, dateofbirth, projectid_val = request.POST.get('firstname'), request.POST.get('lastname'), request.POST.get('dateofbirth'), request.POST.get('projectid')
        patient_new = False
        # get patient
        # return HttpResponse(json.dumps(response))
        try:
            patient = Patient.objects.get(firstname = firstname, lastname = lastname, dateofbirth = dateofbirth)
            # check if patient already exist in project
            if patient.projectid_patient.filter(project_id = project_pk).exists():
                messages.error(request, 'Patient already registered for this project')
                return return_page
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
                # messages.error(request, e)
                # messages.error(request, 'Error in accessing project specific id')
                # return return_page
                # create projectid
                projectid = ProjectId(project_id = project_pk, patient_id = patient.pk, projectid = projectid_val)
                projectid.save()
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
                datapoint_pks = []
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
                            # PatientDatapoint.objects.filter(pk__in = datapoint_pks).delete()
                            [p.delete() for p in PatientDatapoint.objects.filter(pk__in = datapoint_pks)]
                            messages.error(request, response['message'])
                            return return_page
                    datapoint = PatientDatapoint(patientdpts = patientdpts, value = ivalue)
                    datapoint.save()
                    datapoint_pks.append(datapoint.pk)
                    patientinfo.datapoints.add(datapoint)
            except Exception as e:
                if patient_new:
                    patientinfo.delete()
                    patient.delete()
                messages.error(request, e)
                messages.error(request, 'Error in adding patient info values')
                return return_page
        #new
        messages.success(request, 'Success')
    elif access_type == 'remove':
        projectid_pks = request.POST.get('projectid_pks')
        force_delete = request.POST.get('force_delete')
        if projectid_pks == "":
            messages.error(request, 'Selected patient(s) not registered to the current project')
            return return_page
        projectid_pks = projectid_pks.split(',')
        try:
            for projectid in ProjectId.objects.filter(pk__in = projectid_pks, project_id = project_pk):
                patient = projectid.patient
                # force_delete
                if force_delete:
                    samples = projectid.sample_projectid.all()
                    for sample in samples:
                        [g.delete() for g in sample.geneanalysis_sample.all()]
                        [c.delete() for c in sample.chipsetanalysis_sample.all()]
                        sample.delete()
                projectid.delete()
                if not patient.projectid_patient.exists():
                    patient.delete()
            messages.success(request, 'Success')
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in deleting selected patients')
    elif access_type == 'edit':
        firstname, lastname, dateofbirth, projectid_val, projectid_pk = request.POST.get('id_firstname'), request.POST.get('id_lastname'), request.POST.get('id_dateofbirth'), request.POST.get('id_projectid'), request.POST.get('projectid_pk')
        # get projectid
        try:
            projectid = ProjectId.objects.prefetch_related('patient').get(pk = projectid_pk)
            projectid_projectid_old = projectid.projectid
            # check project and projectid
            if int(projectid.project_id) != int(project_pk):
                messages.error(request, 'Patient does not belong to the current project')
            try:
                projectid.projectid = projectid_val
                projectid.save()
            except Exception as e:
                messages.error(request, e)
                messages.error(request, 'Error in editing projectid')
                return return_page
            try:
                projectid.patient.firstname = firstname
                projectid.patient.lastname = lastname
                projectid.patient.dateofbirth = dateofbirth
                projectid.patient.save()
                messages.success(request, 'Success')
            except:
                # reset projectid
                projectid.projectid = projectid_projectid_old
                projectid.save()
                messages.error(request, 'Error in editing patient information')
                return return_page
        except:
            messages.error(request, 'Error in accessing requested patient')
            return HttpResponseRedirect(reverse('patients_view_user', kwargs = dict(project_pk = project_pk)))
    return return_page

@login_required
def patient_view_user(request, projectid_pk):
    return_page = HttpResponseRedirect(reverse('projects_view_user'))
    # new
    try:
        projectid = ProjectId.objects.prefetch_related('patient').get(pk = projectid_pk)
    except:
        messages.error(request, 'Selected patient is not accessible')
        return return_page
    # check user
    response = fn_auth_project_user(request.user, projectid.project_id)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    try:
        sampledpts = list(projectid.project.samplespec.sampledpts_samplespec.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
    except:
        sampledpts = []
    formsample = SampleAddForm()
    return render(request, 'ui_new/user/patients/patient.html', dict(project_pk = projectid.project_id, projects = projects, projectid = projectid, sampledpts = json.dumps(sampledpts), formsample = formsample, current_page = 'patient', current_line = 'patients'))