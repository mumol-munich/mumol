from django.shortcuts import render
from django.urls import reverse
from django.http.response import HttpResponse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

import json

from ..models import Project, Sample, Specification, ChipsetSpecification, SpecDPTs, ConfDPTs, Datapoint, GeneAnalysis, ChipsetAnalysis, ChipsetDatapoint
from ..functions import fn_checkvalidator, fn_create_or_get_none_datapointtype, fn_auth_project_user
from ..config import content


@login_required
def gene_analysis_add(request, sample_pk):
    genespec_pk = request.GET.get('genespec')
    custom_return_page = request.GET.get('return')
    if request.method == 'POST':
        return_page = HttpResponseRedirect(str(reverse('gene_analysis_add', kwargs = dict(sample_pk = sample_pk)) + '?genespec=' + str(genespec_pk)))
        return_page_success = HttpResponseRedirect(str(reverse('gene_analysis_add', kwargs = dict(sample_pk = sample_pk))))
        if custom_return_page:
            return_page = HttpResponseRedirect(str(reverse('gene_analysis_add', kwargs = dict(sample_pk = sample_pk)) + '?genespec=' + str(genespec_pk) + '&return=' + str(custom_return_page)))
            sample = Sample.objects.get(pk = sample_pk)
            project_pk = sample.projectid.project_id
            if custom_return_page == 'samples_overview':
                return_page_success = HttpResponseRedirect(str(reverse('samples_view_user', kwargs = dict(project_pk = project_pk)) + '?genespec=' + str(genespec_pk)))
        try:
            specdpts_pks = request.POST.get('custom_pks').split(',')
        except:
            # no datapoints for this analysis
            specdpts_pks = []
        try:
            # create gene analysis
            geneanalysis = GeneAnalysis(sample_id = sample_pk, specification_id = genespec_pk)
            geneanalysis.save()
        except:
            messages.error(request, 'Gene analysis already exist')
            return return_page
        if specdpts_pks:
            # with datapoints
            try:
                for specdpts_pk in specdpts_pks:
                    key = f'custom_{specdpts_pk}'
                    specdpts = SpecDPTs.objects.get(pk = specdpts_pk, specification_id = genespec_pk)
                    ivalue = request.POST.get(key)
                    if specdpts.datapointtype.type == 'multiple':
                        ivalue = request.POST.getlist(key)
                        ivalue = ','.join(ivalue)
                    if ivalue == "":
                        continue
                    # check validators
                    response = fn_checkvalidator(ivalue, specdpts.datapointtype)
                    if not response['ok']:
                        geneanalysis.delete()
                        messages.error(request, response['message'])
                        return return_page
                    datapoint = Datapoint(specdpts_id = specdpts_pk, value = ivalue)
                    datapoint.save()
                    geneanalysis.datapoints.add(datapoint)
                messages.success(request, 'Success')
                return return_page_success
            except Exception as e:
                geneanalysis.delete()
                messages.error(request, e)
                messages.error(request, 'Error in adding gene analysis values')
                return return_page
        else:
            # without datapoints
            try:
                dpt_pk = fn_create_or_get_none_datapointtype() 
                specdpts = SpecDPTs.objects.get(specification_id = genespec_pk, datapointtype_id = dpt_pk)
                datapoint = Datapoint(specdpts_id = specdpts.pk)
                datapoint.save()
                geneanalysis.datapoints.add(datapoint)
                messages.success(request, 'Success')
                return return_page_success
            except Exception as e:
                geneanalysis.delete()
                messages.error(request, e)
                return return_page
    genespec = False
    currentdpts = []
    specdpts = []
    current_page = 'add_geneanalysis'
    if genespec_pk:
        current_page = 'add_geneanalysis_form'
        try:
            genespec = Specification.objects.prefetch_related('specdpts_specification', 'specdpts_specification__datapointtype').get(pk = genespec_pk)
            specdpts = list(genespec.specdpts_specification.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
            try:
                currentdpts = list(genespec.geneanalysis_specification.get(sample_id = sample_pk).datapoints.values())
                messages.info(request, 'Selected gene analysis already exist for this patient')
            except:
                currentdpts = []
        except:
            messages.error(request, 'Error in accessing requested gene specification')
            return HttpResponseRedirect(reverse('gene_analysis_add', kwargs = dict(sample_pk = sample_pk)))
    return_page = HttpResponseRedirect(reverse('projects_view_user'))
    try:
        sample = Sample.objects.prefetch_related('projectid', 'projectid__project').get(pk = sample_pk)
        project_pk = sample.projectid.project_id
        # check user
        response = fn_auth_project_user(request.user, project_pk)
        if not response['ok']:
            messages.error(request, response['message'])
            return response['return_page']
    except:
        messages.error(request, 'Error in accessing requested sample')
        return return_page
    if genespec_pk:
        genespecs = []
    else:
        genespecs = list(sample.projectid.project.specification_project.order_by('method__name', 'gene__name', 'status').values('pk', 'method_id', 'method__name', 'gene_id', 'gene__name', 'status'))
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    return render(request, 'ui_new/user/gene_analysis/gene_analysis_add.html', dict(project_pk = project_pk, projects = projects, sample = sample, projectid = sample.projectid, genespecs = json.dumps(genespecs), genespec = genespec, currentdpts = currentdpts, specdpts = json.dumps(specdpts), custom_return_page = custom_return_page, current_page = current_page, current_line = 'patients'))

@login_required
def chipset_analysis_add(request, sample_pk):
    chipsetspec_pk = request.GET.get('chipsetspec')
    custom_return_page = request.GET.get('return')
    if request.method == 'POST':
        return_page = HttpResponseRedirect(str(reverse('chipset_analysis_add', kwargs = dict(sample_pk = sample_pk)) + '?chipsetspec=' + str(chipsetspec_pk)))
        return_page_success = HttpResponseRedirect(str(reverse('chipset_analysis_add', kwargs = dict(sample_pk = sample_pk))))
        if custom_return_page:
            return_page = HttpResponseRedirect(str(reverse('chipset_analysis_add', kwargs = dict(sample_pk = sample_pk)) + '?chipsetspec=' + str(chipsetspec_pk) + '&return=' + str(custom_return_page)))
            sample = Sample.objects.get(pk = sample_pk)
            project_pk = sample.projectid.project_id
            if custom_return_page == 'samples_overview':
                return_page_success = HttpResponseRedirect(str(reverse('samples_view_user', kwargs = dict(project_pk = project_pk)) + '?chipsetspec=' + str(chipsetspec_pk)))
        try:
            gene_confdpt_dict = json.loads(request.POST.get('custom_pks'))
        except:
            # no datapoints for this analysis
            gene_confdpt_dict = []
        try:
            # create chipset analysis
            chipsetanalysis = ChipsetAnalysis(sample_id = sample_pk, chipsetspec_id = chipsetspec_pk)
            chipsetanalysis.save()
        except:
            messages.error(request, 'Chipset analysis already exist')
            return return_page
        if gene_confdpt_dict:
            # with datapoints
            try:
                for gene_confdpt in gene_confdpt_dict:
                    gene_pk = gene_confdpt["gene_pk"]
                    confdpts_pk = gene_confdpt["confdpt_pk"]
                    key = f'custom_{gene_pk}_{confdpts_pk}'
                    confdpts = ConfDPTs.objects.get(pk = confdpts_pk, chipsetspec_id = chipsetspec_pk)
                    ivalue = request.POST.get(key)
                    if confdpts.datapointtype.type == 'multiple':
                        ivalue = request.POST.getlist(key)
                        ivalue = ','.join(ivalue)
                    if ivalue == "":
                        continue
                    # check validators
                    response = fn_checkvalidator(ivalue, confdpts.datapointtype)
                    if not response['ok']:
                        chipsetanalysis.delete()
                        messages.error(request, response['message'])
                        return return_page
                    datapoint = ChipsetDatapoint(gene_id = gene_pk, confdpts_id = confdpts_pk, value = ivalue)
                    datapoint.save()
                    chipsetanalysis.datapoints.add(datapoint)
                messages.success(request, 'Success')
                return return_page_success
            except Exception as e:
                chipsetanalysis.delete()
                messages.error(request, e)
                messages.error(request, 'Error in adding chipset analysis values')
                return return_page
        else:
            # without datapoints
            chipsetanalysis.delete()
            messages.error(request, 'No datapoint types available. This is not possible for chipset analysis')
            return return_page
    chipsetspec = False
    confdpts = []
    currentdpts = []
    current_page = 'add_chipsetanalysis'
    if chipsetspec_pk:
        current_page = 'add_chipsetanalysis_form'
        try:
            chipsetspec = ChipsetSpecification.objects.prefetch_related('confdpts_chipsetspec', 'confdpts_chipsetspec__datapointtype').get(pk = chipsetspec_pk)
            confdpts = list(chipsetspec.confdpts_chipsetspec.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
            try:
                currentdpts = list(chipsetspec.chipsetanalysis_chipsetspec.get(sample_id = sample_pk).datapoints.values())
                messages.info(request, 'Selected chipset analysis already exist for this patient')
            except:
                currentdpts = []
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in accessing requested chipset specification')
            return HttpResponseRedirect(reverse('chipset_analysis_add', kwargs = dict(sample_pk = sample_pk)))
    return_page = HttpResponseRedirect(reverse('projects_view_user'))
    try:
        sample = Sample.objects.prefetch_related('projectid', 'projectid__project').get(pk = sample_pk)
        project_pk = sample.projectid.project_id
        # check user
        response = fn_auth_project_user(request.user, project_pk)
        if not response['ok']:
            messages.error(request, response['message'])
            return response['return_page']
    except:
        messages.error(request, 'Error in accessing requested sample')
        return return_page
    chipsetspecs = sample.projectid.project.chipsetspec_project.order_by('-pk')
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    return render(request, 'ui_new/user/chipset_analysis/chipset_analysis_add.html', dict(project_pk = project_pk, projects = projects, sample = sample, projectid = sample.projectid, chipsetspecs = chipsetspecs, chipsetspec = chipsetspec, confdpts = confdpts, currentdpts = currentdpts, custom_return_page = custom_return_page, current_page = current_page, current_line = 'patients'))