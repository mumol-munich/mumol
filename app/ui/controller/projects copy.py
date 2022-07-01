from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from ..models import ChipsetAnalysis, PatientDPTs, SampleDPTs, Project, User, GeneAnalysis, DatapointType
from ..decorators import admin_required
from ..forms import ProjectAddForm
from ..functions import fn_convert_genespec_json, fn_auth_project_user


# user
@login_required
def projects_view_user(request):
    project_redirect = request.GET.get('project_redirect')
    analysis_type = request.GET.get('type')
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
    else:
        chipsetanalyses = ChipsetAnalysis.objects.filter(sample__projectid__project_id__in = list(projects.values_list('id', flat = True)))
    datapointtypes = DatapointType.objects.values('pk', 'name')
    return render(request, 'ui_new/user/projects/projects.html', dict(projects = projects, geneanalyses = geneanalyses, chipsetanalyses = chipsetanalyses, analysis_type = analysis_type, datapointtypes = datapointtypes, project_link_deny = True, project_redirect = project_redirect, first_project_id = first_project_id, patientdpts = patientdpts, sampledpts = sampledpts))

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