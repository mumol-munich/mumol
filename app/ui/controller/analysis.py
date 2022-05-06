from django.shortcuts import render
from django.urls import reverse
from django.http.response import HttpResponse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import json
from numpy import NAN

import pandas as pd
from io import BytesIO

from ..models import Project, Sample, Specification, ChipsetSpecification, SpecDPTs, ConfDPTs, Datapoint, GeneAnalysis, ChipsetAnalysis, ChipsetDatapoint, DatapointsRow
from ..functions import fn_checkvalidator, fn_create_or_get_none_datapointtype, fn_auth_project_user
from ..config import content

# new
@login_required
def analysis_genes_view(request, project_pk):
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    project_pks = [p.pk for p in projects]
    # geneanalyses = GeneAnalysis.objects.filter(sample__projectid__project_id__in = project_pks)
    geneanalyses = GeneAnalysis.objects.filter(sample__projectid__project_id = project_pk)
    return render(request, 'ui_new/user/analysis/gene_analysis_overview.html', dict(projects = projects, project_pk = project_pk, geneanalyses = geneanalyses, current_page = "patients", current_line = "geneanalyses"))

@login_required
@require_http_methods(['POST'])
def analysis_genes_overview_remove(request, project_pk):
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    access_type = request.POST.get('access_type')
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    if access_type == 'remove':
        geneanalysis_pks = request.POST.get('geneanalysis_pks').split(',')
        try:
            # GeneAnalysis.objects.filter(pk__in = geneanalysis_pks).delete()
            [g.delete() for g in GeneAnalysis.objects.filter(pk__in = geneanalysis_pks)]
            messages.success(request, 'Success')
        except Exception as e:
            messages.error(request, e)
    else:
        messages.error(request, 'Error accessing information')
    return return_page

@login_required
def analysis_genes_add_remove(request, sample_pk):
    genespec_pk = request.GET.get('genespec')
    custom_return_page = request.GET.get('return')
    return_page = HttpResponseRedirect(reverse('projects_view_user'))
    return_page_success = return_page
    # check sample
    try:
        sample = Sample.objects.prefetch_related('projectid', 'projectid__project').get(pk = sample_pk)
        project_pk = sample.projectid.project_id
        response = fn_auth_project_user(request.user, project_pk)
        if not response['ok']:
            messages.error(request, response['message'])
            return response['return_page']
        return_page = HttpResponseRedirect(str(reverse('analysis_genes_add_remove', kwargs = dict(sample_pk = sample_pk)) + '?genespec=' + str(genespec_pk)))
        if custom_return_page:
            return_page = HttpResponseRedirect(str(reverse('analysis_genes_add_remove', kwargs = dict(sample_pk = sample_pk)) + '?genespec=' + str(genespec_pk) + '&return=' + str(custom_return_page)))
        return_page_success = HttpResponseRedirect(reverse('sample_view_user', kwargs=dict(sample_pk = sample_pk)))
    except:
        messages.error(request, 'Error in accessing requested sample')
        return return_page
    if request.method == 'POST':
        access_type = request.POST.get('access_type')
        if custom_return_page == 'samples_overview':
            return_page_success =  HttpResponseRedirect(str(reverse('samples_view_user', kwargs = dict(project_pk = project_pk)) + '?genespec=' + str(genespec_pk)))
        elif custom_return_page == 'sample':
            return_page_success = HttpResponseRedirect(reverse('sample_view_user', kwargs = dict(sample_pk = sample_pk)))
        elif custom_return_page == 'geneanalysis_overview':
            return_page_success = HttpResponseRedirect(reverse('analysis_genes_view', kwargs = dict(project_pk = project_pk)))
        try:
            specdpts_pks = request.POST.get('custom_pks').split(',')
        except:
            # no datapoints for this analysis
            specdpts_pks = []
        try:
            datapointsrow_pks = request.POST.get('custom_counter_ids').split(',')
        except:
            # no datapointsrow for this analysis
            datapointsrow_pks = []
        # new
        if access_type == 'add':
            try:
                # create gene analysis
                geneanalysis = GeneAnalysis(sample_id = sample_pk, specification_id = genespec_pk)
                geneanalysis.save()
            except:
                messages.error(request, 'Gene analysis already exist. Please click edit button to enable editing')
                return return_page
            # new
            if specdpts_pks:
                # with datapoints
                for datapointsrow_pk in datapointsrow_pks:
                    datapointsrow = DatapointsRow()
                    datapointsrow.save()
                    try:
                        for specdpts_pk in specdpts_pks:
                            key = f'custom_add_{datapointsrow_pk}_{specdpts_pk}'
                            specdpts = SpecDPTs.objects.get(pk = specdpts_pk, specification_id = genespec_pk)
                            ivalue = request.POST.get(key)
                            if specdpts.datapointtype.type == 'multiple':
                                ivalue = request.POST.getlist(key)
                                ivalue = ','.join(ivalue)
                            if specdpts.mandatory and not ivalue:
                                messages.error(request, 'Mandatory field is not filled')
                                return return_page
                            if ivalue:
                                # check validators
                                response = fn_checkvalidator(ivalue, specdpts.datapointtype)
                                if not response['ok']:
                                    geneanalysis.delete()
                                    messages.error(request, response['message'])
                                    messages.error('test')
                                    return return_page
                            datapoint = Datapoint(specdpts_id = specdpts_pk, value = ivalue)
                            datapoint.save()
                            datapointsrow.datapoints.add(datapoint)
                        geneanalysis.datapointsrows.add(datapointsrow)
                    except Exception as e:
                        datapointsrow.delete()
                        geneanalysis.delete()
                        messages.error(request, e)
                        messages.error(request, 'Error in adding gene analysis values')
                messages.success(request, 'Success')
                return return_page_success
            else:
                # without datapoints
                try:
                    dpt_pk = fn_create_or_get_none_datapointtype()
                    specdpts = SpecDPTs.objects.get(specification_id = genespec_pk, datapointtype_id = dpt_pk)
                    datapoint = Datapoint(specdpts_id = specdpts.pk)
                    datapoint.save()
                    datapointsrow = DatapointsRow()
                    datapointsrow.save()
                    datapointsrow.datapoints.add(datapoint)
                    geneanalysis.datapointsrows.add(datapointsrow)
                    messages.success(request, 'Success')
                    return return_page_success
                except Exception as e:
                    geneanalysis.delete()
                    messages.error(request, e)
                    return return_page
            # # new
            # if specdpts_pks:
            #     # with datapoints
            #     try:
            #         for specdpts_pk in specdpts_pks:
            #             key = f'custom_{specdpts_pk}'
            #             specdpts = SpecDPTs.objects.get(pk = specdpts_pk, specification_id = genespec_pk)
            #             ivalue = request.POST.get(key)
            #             if specdpts.datapointtype.type == 'multiple':
            #                 ivalue = request.POST.getlist(key)
            #                 ivalue = ','.join(ivalue)
            #             if specdpts.mandatory and not ivalue:
            #                 messages.error(request, 'Mandatory field is not filled')
            #                 return return_page
            #             if ivalue:
            #                 # check validators
            #                 response = fn_checkvalidator(ivalue, specdpts.datapointtype)
            #                 if not response['ok']:
            #                     geneanalysis.delete()
            #                     messages.error(request, response['message'])
            #                     return return_page
            #             datapoint = Datapoint(specdpts_id = specdpts_pk, value = ivalue)
            #             datapoint.save()
            #             geneanalysis.datapoints.add(datapoint)
            #         messages.success(request, 'Success')
            #         return return_page_success
            #     except Exception as e:
            #         geneanalysis.delete()
            #         messages.error(request, e)
            #         messages.error(request, 'Error in adding gene analysis values')
            #         return return_page
            # else:
            #     # without datapoints
            #     try:
            #         dpt_pk = fn_create_or_get_none_datapointtype() 
            #         specdpts = SpecDPTs.objects.get(specification_id = genespec_pk, datapointtype_id = dpt_pk)
            #         datapoint = Datapoint(specdpts_id = specdpts.pk)
            #         datapoint.save()
            #         geneanalysis.datapoints.add(datapoint)
            #         messages.success(request, 'Success')
            #         return return_page_success
            #     except Exception as e:
            #         geneanalysis.delete()
            #         messages.error(request, e)
            #         return return_page
        elif access_type == 'edit':
            try:
                # get gene analysis
                geneanalysis = GeneAnalysis.objects.get(sample_id = sample_pk, specification_id = genespec_pk)
            except:
                messages.error(request, 'Error in accessing requested gene analysis')
                return return_page
            # new
            if specdpts_pks:
                # with datapoints
                for datapointsrow_pk in datapointsrow_pks:
                    datapointsrow_new = False
                    try:
                        # get existing datapointsrow for editing
                        datapointsrow = DatapointsRow.objects.get(pk = datapointsrow_pk)
                    except:
                        # create datapointsrow if not exist
                        datapointsrow = DatapointsRow()
                        datapointsrow.save()
                        geneanalysis.datapointsrows.add(datapointsrow)
                        datapointsrow_new = True
                    try:
                        for specdpts_pk in specdpts_pks:
                            key = f'custom_add_{datapointsrow_pk}_{specdpts_pk}'
                            specdpts = SpecDPTs.objects.get(pk = specdpts_pk, specification_id = genespec_pk)
                            ivalue = request.POST.get(key)
                            if specdpts.datapointtype.type == 'multiple':
                                ivalue = request.POST.getlist(key)
                                ivalue = ','.join(ivalue)
                            if specdpts.mandatory and not ivalue:
                                messages.error(request, 'Mandatory field is not filled')
                                return return_page
                            if ivalue:
                                # check validators
                                response = fn_checkvalidator(ivalue, specdpts.datapointtype)
                                if not response['ok']:
                                    geneanalysis.delete()
                                    messages.error(request, response['message'])
                                    messages.error('test')
                                    return return_page
                            try:
                                datapoint = datapointsrow.datapoints.get(specdpts_id = specdpts.pk)
                                datapoint.value = ivalue
                                datapoint.save()
                            except:
                                datapoint = Datapoint(specdpts_id = specdpts_pk, value = ivalue)
                                datapoint.save()
                                datapointsrow.datapoints.add(datapoint)
                    except Exception as e:
                        messages.error(request, e)
                        messages.error(request, 'Error in editing gene analysis datapiont values')
                        if datapointsrow_new:
                            datapointsrow.delete()
                        return return_page
                messages.success(request, 'Success')
                return return_page_success
            else:
                # without datapoints
                messages.warning(request, 'No datapoints available for editing')
                return return_page
            # new
            # if specdpts_pks:
            # # with datapoints
            #     try:
            #         for specdpts_pk in specdpts_pks:
            #             key = f'custom_{specdpts_pk}'
            #             specdpts = SpecDPTs.objects.get(pk = specdpts_pk, specification_id = genespec_pk)
            #             ivalue = request.POST.get(key)
            #             if specdpts.datapointtype.type == 'multiple':
            #                 ivalue = request.POST.getlist(key)
            #                 ivalue = ','.join(ivalue)
            #             if specdpts.mandatory and not ivalue:
            #                 messages.error(request, 'Mandatory field is not filled')
            #                 return return_page
            #             if ivalue:
            #                 # check validators
            #                 response = fn_checkvalidator(ivalue, specdpts.datapointtype)
            #                 if not response['ok']:
            #                     # geneanalysis.delete()
            #                     messages.error(request, response['message'])
            #                     return return_page
            #             try:
            #                 datapoint = geneanalysis.datapoints.get(specdpts_id = specdpts.pk)
            #                 datapoint.value = ivalue
            #                 datapoint.save()
            #             except:
            #                 datapoint = Datapoint(specdpts_id = specdpts_pk, value = ivalue)
            #                 datapoint.save()
            #                 geneanalysis.datapoints.add(datapoint)
            #         messages.success(request, 'Success')
            #         return return_page_success
            #     except Exception as e:
            #         # geneanalysis.delete()
            #         messages.error(request, e)
            #         messages.error(request, 'Error in editing gene analysis datapiont values')
            #         return return_page
            # else:
            #     # without datapoints
            #     messages.warning(request, 'No datapoints available for editing')
            #     return return_page
        elif access_type == 'remove':
            geneanalysis_pks = request.POST.get('gene_analysis_pks')
            try:
                geneanalysis = GeneAnalysis(sample_id = sample_pk, pk = geneanalysis_pks)
                geneanalysis.delete()
                messages.success(request, 'Success')
                return return_page_success
            except:
                messages.error(request, 'Error in deleting selected gene analysis')
                return return_page
    genespec = False
    genespecs = []
    # currentdpts = []
    currentdptsrows = []
    specdpts = []
    current_page = 'add_geneanalysis'
    if genespec_pk:
        current_page = 'add_geneanalysis_form'
        try:
            genespec = Specification.objects.prefetch_related('specdpts_specification', 'specdpts_specification__datapointtype').get(pk = genespec_pk)
            specdpts = list(genespec.specdpts_specification.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
            # try:
            #     currentdpts = list(genespec.geneanalysis_specification.get(sample_id = sample_pk).datapoints.values())
            #     if not request.GET.get("edit"):
            #         messages.info(request, 'Selected gene analysis already exist for this patient. Please click edit to modify the info')
            # except:
            #     pass
            try:
                currentdptsrows = list(genespec.geneanalysis_specification.get(sample_id = sample_pk).datapointsrows.prefetch_related('datapoints', 'datapoints__specdpts__datapointtype').values('pk', 'datapoints__id', 'datapoints__specdpts_id', 'datapoints__value', 'datapoints__specdpts__datapointtype__type'))
                if not request.GET.get("edit"):
                    messages.info(request, 'Selected gene analysis already exist for this patient. Please click edit to modify the info')
            except:
                pass
        except:
            messages.error(request, 'Error in accessing requested gene specification')
            return return_page
    else:
        genespecs = list(sample.projectid.project.specification_project.order_by('method__name', 'gene__name', 'status').values('pk', 'method_id', 'method__name', 'gene_id', 'gene__name', 'status'))
    # check user
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    return render(request, 'ui_new/user/analysis/gene_analysis_add.html', dict(project_pk = project_pk, projects = projects, sample = sample, projectid = sample.projectid, genespecs = json.dumps(genespecs), genespec = genespec, currentdptsrows = currentdptsrows, specdpts = json.dumps(specdpts), custom_return_page = custom_return_page, current_page = current_page, current_line = 'patients'))

@login_required
def analysis_chipsets_view(request, project_pk):
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    project_pks = [p.pk for p in projects]
    # chipsetanalyses = ChipsetAnalysis.objects.filter(sample__projectid__project_id__in = project_pks)
    chipsetanalyses = ChipsetAnalysis.objects.filter(sample__projectid__project_id = project_pk)
    return render(request, 'ui_new/user/analysis/chipset_analysis_overview.html', dict(projects = projects, project_pk = project_pk, chipsetanalyses = chipsetanalyses, current_page = "patients", current_line = "chipsetanalyses"))

@login_required
@require_http_methods(['POST'])
def analysis_chipsets_overview_remove(request, project_pk):
    # check user
    response = fn_auth_project_user(request.user, project_pk)
    if not response['ok']:
        messages.error(request, response['message'])
        return response['return_page']
    access_type = request.POST.get('access_type')
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    if access_type == 'remove':
        chipsetanalysis_pks = request.POST.get('chipsetanalysis_pks').split(',')
        try:
            # ChipsetAnalysis.objects.filter(pk__in = chipsetanalysis_pks).delete()
            [c.delete() for c in ChipsetAnalysis.objects.filter(pk__in = chipsetanalysis_pks)]
            messages.success(request, 'Success')
        except Exception as e:
            messages.error(request, e)
    else:
        messages.error(request, 'Error accessing information')
    return return_page

@login_required
def analysis_chipsets_upload_download(request, sample_pk):
    chipsetspec_pk = request.GET.get('chipsetspec')
    return_page = HttpResponseRedirect(reverse('analysis_chipsets_add_remove', kwargs = dict(sample_pk = sample_pk)) + '?chipsetspec=' + chipsetspec_pk + '&edit=true')
    try:
        chipsetspec = ChipsetSpecification.objects.get(pk = chipsetspec_pk)
    except:
        messages.error(request, 'Error in accessing requested gene analysis')
        return return_page
    try:
        # get chipset analysis
        chipsetanalysis = ChipsetAnalysis.objects.get(sample_id = sample_pk, chipsetspec_id = chipsetspec_pk)
    except:
        chipsetanalysis = False
    if request.method == 'POST':
        chipsetanalysis_new = False
        ftab = pd.read_csv(request.FILES['upload_chipsetanalysis_batch_file'], sep = '\t', dtype=str)
        ftab = ftab.fillna('')
        ftabheader = list(ftab.columns)
        ftabmandatory = list(chipsetspec.confdpts_chipsetspec.filter(mandatory = True).values_list('datapointtype__name', flat = True))
        if len(ftabheader) != len(set(ftabheader)):
            messages.error(request, 'Duplicate column names found in the header')
            return return_page
        if not 'GENES' in ftabheader:
            messages.error(request, 'Uploaded file did not contain the column GENES. Please use a valid template.')
            return return_page
        ftabheader.remove('GENES')
        # check mandatory columns
        for ftabm in ftabmandatory:
            if ftabm not in ftabheader:
                messages.error(request, 'Mandatory columns must be present in the uploaded file')
                return return_page
        if not chipsetanalysis:
            chipsetanalysis = ChipsetAnalysis(sample_id = sample_pk, chipsetspec_id = chipsetspec_pk)
            chipsetanalysis.save()
            chipsetanalysis_new = True
        confdpts_pks = []
        for hname in ftabheader:
            try:
                confdpts = chipsetspec.confdpts_chipsetspec.get(datapointtype__name = hname.strip())
                confdpts_pks.append(confdpts.pk)
            except Exception as e:
                messages.error(request, e)
                messages.error(request, f'Unknown column name {hname} in the uploaded file')
                return return_page
        for fgene in ftab.GENES:
            gene = chipsetspec.genes.filter(name = fgene).first()
            if gene:
                for confdpts_pk in confdpts_pks:
                    confdpts = ConfDPTs.objects.get(pk = confdpts_pk)
                    ivalue = (ftab[ftab['GENES'] == fgene][confdpts.datapointtype.name]).values[0]
                    if confdpts.mandatory and not ivalue:
                        messages.error(request, f'Mandatory field "{confdpts.datapointtype.name}" is not filled')
                        return return_page
                    if ivalue:
                        # check validators
                        response = fn_checkvalidator(ivalue, confdpts.datapointtype)
                        if not response['ok']:
                            if chipsetanalysis_new:
                                chipsetanalysis.delete()
                            messages.error(request, response['message'])
                            return return_page
                        # check value
                        if confdpts.datapointtype.type in ['boolean', 'select', 'multiple']:
                            if not all([i in confdpts.datapointtype.options.split(',') for i in ivalue.split(',')]):
                                if chipsetanalysis_new:
                                    chipsetanalysis.delete()
                                messages.error(request, f'Invalid options selected in "{confdpts.datapointtype.name}"')
                                return return_page
                        datapoint = ChipsetDatapoint(gene_id = gene.pk, confdpts_id = confdpts.pk, value = ivalue)
                        datapoint.save()
                        chipsetanalysis.datapoints.add(datapoint)
        messages.success(request, 'Success')
        return return_page
    # download template
    fgenelist = list(chipsetspec.genes.values_list('name', flat = True))
    fdatapointtypes = list(chipsetspec.confdpts_chipsetspec.values_list('datapointtype__name', flat = True))
    ftab = '\t'.join(['GENES'] + fdatapointtypes) + '\n'
    if chipsetanalysis:
        for fgene in fgenelist:
            ftab += '\t'.join([fgene] + list(chipsetanalysis.datapoints.filter(gene__name = fgene).values_list('value', flat = True))) + '\n'
    else:
        fdatapointtypes_def = list(chipsetspec.confdpts_chipsetspec.values_list('default', flat = True))
        for fgene in fgenelist:
            ftab += '\t'.join([fgene] + fdatapointtypes_def) + '\n'
    response = HttpResponse(ftab, content_type = 'application/vnd.ms-excel')
    response['Content-Disposition'] = 'inline; filename=chipsetanalysis_template.txt'
    return response
    return return_page

@login_required
def analysis_chipsets_add_remove(request, sample_pk):
    chipsetspec_pk = request.GET.get('chipsetspec')
    custom_return_page = request.GET.get('return')
    return_page = HttpResponseRedirect(reverse('projects_view_user'))
    return_page_success = return_page
    # check sample
    try:
        sample = Sample.objects.prefetch_related('projectid', 'projectid__project').get(pk = sample_pk)
        project_pk = sample.projectid.project_id
        response = fn_auth_project_user(request.user, project_pk)
        if not response['ok']:
            messages.error(request, response['message'])
            return response['return_page']
        return_page = HttpResponseRedirect(str(reverse('analysis_chipsets_add_remove', kwargs = dict(sample_pk = sample_pk)) + '?chipsetspec=' + str(chipsetspec_pk)))
        if custom_return_page:
            return_page = HttpResponseRedirect(str(reverse('analysis_chipsets_add_remove', kwargs = dict(sample_pk = sample_pk)) + '?chipsetspec=' + str(chipsetspec_pk) + '&return=' + str(custom_return_page)))
        return_page_success = HttpResponseRedirect(reverse('sample_view_user', kwargs=dict(sample_pk = sample_pk)))
    except:
        messages.error(request, 'Error in accessing requested sample')
        return return_page
    if request.method == 'POST':
        access_type = request.POST.get('access_type')
        if custom_return_page == 'samples_overview':
            return_page_success = HttpResponseRedirect(str(reverse('samples_view_user', kwargs = dict(project_pk = project_pk)) + '?chipsetspec=' + str(chipsetspec_pk)))
        elif custom_return_page == 'sample':
            return_page_success = HttpResponseRedirect(reverse('sample_view_user', kwargs = dict(sample_pk = sample_pk)))
        elif custom_return_page == 'chipsetanalysis_overview':
            return_page_success = HttpResponseRedirect(reverse('analysis_chipsets_view', kwargs = dict(project_pk = project_pk)))
        try:
            gene_confdpt_dict = json.loads(request.POST.get('custom_pks'))
        except:
            # no datapoints for this analysis
            gene_confdpt_dict = []
        if access_type == 'add':
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
                        if confdpts.mandatory and not ivalue:
                            messages.error(request, 'Mandatory field is not filled')
                            return return_page
                        if ivalue:
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
        elif access_type == 'edit':
            try:
                # get chipset analysis
                chipsetanalysis = ChipsetAnalysis.objects.get(sample_id = sample_pk, chipsetspec_id = chipsetspec_pk)
            except:
                messages.error(request, 'Error in accessing requested gene analysis')
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
                        if confdpts.mandatory and not ivalue:
                            messages.error(request, 'Mandatory field is not filled')
                            return return_page
                        if ivalue:
                            # check validators
                            response = fn_checkvalidator(ivalue, confdpts.datapointtype)
                            if not response['ok']:
                                # chipsetanalysis.delete()
                                messages.error(request, response['message'])
                                return return_page
                        datapoint = chipsetanalysis.datapoints.filter(confdpts_id = confdpts.pk).last()
                        try:
                            datapoint = chipsetanalysis.datapoints.get(confdpts_id = confdpts_pk, gene_id = gene_pk)
                            datapoint.value = ivalue
                            datapoint.save()
                        except:
                            datapoint = ChipsetDatapoint(gene_id = gene_pk, confdpts_id = confdpts_pk, value = ivalue)
                            datapoint.save()
                            chipsetanalysis.datapoints.add(datapoint)
                    messages.success(request, 'Success')
                    return return_page_success
                except Exception as e:
                    # chipsetanalysis.delete()
                    messages.error(request, e)
                    messages.error(request, 'Error in adding chipset analysis values')
                    return return_page
            else:
                # without datapoints
                # chipsetanalysis.delete()
                messages.error(request, 'No datapoint types available. This is not possible for chipset analysis')
                return return_page
        elif access_type == 'remove':
            chipsetanalysis_pks = request.POST.get('chipset_analysis_pks')
            try:
                chipsetanalysis = ChipsetAnalysis(sample_id = sample_pk, pk = chipsetanalysis_pks)
                chipsetanalysis.delete()
                messages.success(request, 'Success')
                return return_page_success
            except:
                messages.error(request, 'Error in deleting selected chipset analysis')
                return return_page
    chipsetspec = False
    currentdpts = []
    confdpts = []
    chipsetspecs = []
    current_page = 'add_chipsetanalysis'
    if chipsetspec_pk:
        current_page = 'add_chipsetanalysis_form'
        try:
            chipsetspec = ChipsetSpecification.objects.prefetch_related('confdpts_chipsetspec', 'confdpts_chipsetspec__datapointtype').get(pk = chipsetspec_pk)
            confdpts = list(chipsetspec.confdpts_chipsetspec.exclude(datapointtype__name = content['default_none']).values('pk', 'mandatory', 'default', 'datapointtype__type', 'datapointtype__name', 'datapointtype__helptext', 'datapointtype__options'))
            try:
                currentdpts = list(chipsetspec.chipsetanalysis_chipsetspec.get(sample_id = sample_pk).datapoints.values())
                if not request.GET.get("edit"):
                    messages.info(request, 'Selected chipset analysis already exist for this patient')
            except:
                pass
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in accessing requested chipset specification')
            return HttpResponseRedirect(reverse('chipset_analysis_add', kwargs = dict(sample_pk = sample_pk)))
    else:
        chipsetspecs = sample.projectid.project.chipsetspec_project.order_by('-pk')
    # check user
    if request.user.profile.is_admin:
        projects = Project.objects.order_by('-pk')
    else:
        projects = request.user.project_user.order_by('-pk')
    return render(request, 'ui_new/user/analysis/chipset_analysis_add.html', dict(project_pk = project_pk, projects = projects, sample = sample, projectid = sample.projectid, chipsetspecs = chipsetspecs, chipsetspec = chipsetspec, confdpts = confdpts, currentdpts = currentdpts, custom_return_page = custom_return_page, current_page = current_page, current_line = 'patients'))
# new
