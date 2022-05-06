from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

import json

from ..config import content
from ..decorators import admin_required
from ..choices import DPVALIDATOR
from ..functions import fn_checkdpts, fn_create_or_get_none_datapointtype, fn_aggregate_rcmd_ids, fn_checkvalidator
from ..models import PatientDPTs, Project, Specification, ChipsetSpecification, SpecDPTs, ConfDPTs, DatapointType, PatientSpecification, SampleSpecification, SampleDPTs, PatientDatapoint, SampleDatapoint, Sample
from ..forms import MethodAddForm, GeneAddForm, SpecificationAddForm, DatapointTypeAddForm, DatapointValidatorAddForm, ChipsetSpecificationAddForm, ProjectAddForm

@login_required
@admin_required
@require_http_methods(['POST'])
def gene_specifications_remove(request, project_pk):
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # window.location.pathname
    if request.POST.get('return_page') == reverse('project_view', kwargs = dict(project_pk = project_pk)):
        genespec_data_level = request.POST.get('custom_genespec_data_level')
        genespec_data_pk = request.POST.get('custom_genespec_data_pk')
        try:
            if genespec_data_level == 'method':
                method_pk = genespec_data_pk
                # Specification.objects.filter(project_id = project_pk, method_id = method_pk).delete()
                [s.delete() for s in Specification.objects.filter(project_id = project_pk, method_id = method_pk)]
            elif genespec_data_level == 'gene':
                method_pk, gene_pk = genespec_data_pk.split(',')
                # Specification.objects.filter(project_id = project_pk, method_id = method_pk, gene_id = gene_pk).delete()
                [s.delete() for s in Specification.objects.filter(project_id = project_pk, method_id = method_pk, gene_id = gene_pk)]
            elif genespec_data_level == 'status':
                genespec_pk = genespec_data_pk
                # Specification.objects.filter(project_id = project_pk, pk = genespec_pk).delete()
                [s.delete() for s in Specification.objects.filter(project_id = project_pk, pk = genespec_pk)]
            else:
                messages.error(request, 'Unknown request')
                return return_page
            messages.success(request, f'Gene specifications associated with selected {genespec_data_level} has been deleted successfully')
        except Exception as e:
            messages.error(request, 'Gene specification has already been linked with results')
            messages.error(request, f'Error in deleting gene specifications associated with selected {genespec_data_level}')
        return return_page
    else:
        pass
    return HttpResponse("HI")

@login_required
@admin_required
def gene_specifications_add(request, project_pk):
    return_page = HttpResponseRedirect(reverse('gene_specifications_add', kwargs = dict(project_pk = project_pk)))
    if request.method == "POST":
        gene_specs = json.loads(request.POST.get("gene_specs"))
        if str(project_pk) != gene_specs['project_pk']:
            messages.error(request, 'Invalid form submitted')
            return return_page
        genespec_pks = []
        # check mutation_status_list
        if not gene_specs['mutation_status_list'] or not gene_specs['mutation_status_dict']:
            messages.error(request, 'Please select at least one result')
            return return_page
        try:
            # iterate through genes
            for gene_pk in gene_specs['id_gene']:
                # iterate through mutation status information
                for status_name, status_value in gene_specs['mutation_status_dict'].items():
                    # create genespec
                    genespec = Specification(project_id = project_pk, gene_id = gene_pk, method_id = gene_specs['id_method'], status = status_name)
                    genespec.save()
                    genespec_pks.append(genespec.pk)
                    if status_value['dpts']:
                        for dpt_pk, dpt_value in status_value.items():
                            if "dpts" in dpt_pk:
                                continue
                            specdpt = SpecDPTs(specification_id = genespec.pk, datapointtype_id = dpt_pk, mandatory = dpt_value['mandatory'], default = dpt_value['default'])
                            specdpt.save() 
                    else:
                        # if no datapoints, create empty specdpt for adding it to gene analysis
                        datapointtype_pk = fn_create_or_get_none_datapointtype()
                        specdpt = SpecDPTs(specification_id = genespec.pk, datapointtype_id = datapointtype_pk)
                        specdpt.save()
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in creating gene specifications')
            # Specification.objects.filter(pk__in = genespec_pks).delete()
            [s.delete() for s in Specification.objects.filter(pk__in = genespec_pks)]
            return return_page
        messages.success(request, 'Success')
        return HttpResponseRedirect(reverse('project_view', kwargs = dict(project_pk = project_pk)))
    formmethod = MethodAddForm()
    formspec = SpecificationAddForm()
    formgene = GeneAddForm()
    formdatatype = DatapointTypeAddForm()
    formvalidator = DatapointValidatorAddForm() 
    projects = Project.objects.order_by('-pk')
    genespecs = list(Specification.objects.filter(project_id = project_pk).values('gene_id', 'method_id', 'status', 'method__name', 'gene__name'))
    # datapointtypes = list(DatapointType.objects.exclude(name = content['default_none']).order_by('-pk').values('pk', 'name', 'options', 'helptext'))
    # 
    # dpts = list(DatapointType.objects.exclude(name = content['default_none']).order_by('-pk').values('pk', 'name', 'options', 'helptext', 'rcmd_methods__id'))
    dpts = list(DatapointType.objects.exclude(name = content['default_none']).order_by('name').values('pk', 'name', 'options', 'helptext', 'rcmd_methods__id'))
    datapointtypes = fn_aggregate_rcmd_ids(dpts)
    # return HttpResponse(datapointtypes)
    #
    statuslist = [s['status'] for s in Specification.objects.values('status').distinct()]
    return render(request, 'ui_new/admin/gene_specifications/gene_specifications_add.html', dict(projects = projects, project_pk = project_pk, formmethod = formmethod, formspec = formspec, formgene = formgene, formdatatype = formdatatype, formvalidator = formvalidator, genespecs = genespecs, chipsetspecs = False, datapointtypes = datapointtypes, DPVALIDATOR = dict(DPVALIDATOR), statuslist = statuslist, project_link_deny = True))

@login_required
@admin_required
def chipset_specifications_add(request, project_pk):
    return_page = HttpResponseRedirect(reverse('chipset_specifications_add', kwargs = dict(project_pk = project_pk)))
    if request.method == 'POST':
        chipset_specs = json.loads(request.POST.get("chipset_specs"))
        # return HttpResponse(json.dumps(chipset_specs))
        if str(project_pk) != chipset_specs['project_pk']:
            messages.error(request, 'Invalid form submitted')
            return return_page
        try:
            chipsetspec = ChipsetSpecification(name = chipset_specs['id_name_chipset'], manufacturer = chipset_specs['id_manufacturer'], version = chipset_specs['id_version'], project_id = project_pk)
            chipsetspec.save()
            try:
                [chipsetspec.genes.add(g) for g in chipset_specs['id_genes']]
                # add confdpts
                confdpt_pks = []
                try:
                    for dpt_pk, value in chipset_specs['dpts_dict'].items():
                        confdpt = ConfDPTs(chipsetspec = chipsetspec, datapointtype_id = dpt_pk, mandatory = value['mandatory'], default = value['default'])
                        confdpt.save()
                        confdpt_pks.append(confdpt.pk)
                    messages.success(request, 'Success')
                except:
                    messages.error(request, 'Error in adding chipset datapoint information')
                    if confdpt_pks:
                        # ConfDPTs.objects.filter(pk__in = confdpt_pks).delete()
                        [c.delete() for c in ConfDPTs.objects.filter(pk__in = confdpt_pks)]
                    chipsetspec.delete()
            except Exception as e:
                chipsetspec.delete()
                messages.error(request, e)
                messages.error(request, 'Error in creating chipset specs')
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in creating Chipset Specification')
        return HttpResponseRedirect(reverse('project_view', kwargs = dict(project_pk = project_pk)))
    formspec = ChipsetSpecificationAddForm()
    formgene = GeneAddForm()
    formdatatype = DatapointTypeAddForm()
    formvalidator = DatapointValidatorAddForm() 
    projects = Project.objects.order_by('-pk')
    chipsetspecs = ChipsetSpecification.objects.filter(project_id = project_pk)
    # datapointtypes = list(DatapointType.objects.exclude(name = content['default_none']).order_by('-pk').values('pk', 'name', 'options', 'helptext'))
    dpts = list(DatapointType.objects.exclude(name = content['default_none']).order_by('name').values('pk', 'name', 'options', 'helptext', 'rcmd_methods__id'))
    datapointtypes = fn_aggregate_rcmd_ids(dpts)
    return render(request, 'ui_new/admin/chipset_specifications/chipset_specifications_add.html', dict(projects = projects, project_pk = project_pk, formspec = formspec, formdatatype = formdatatype, formvalidator = formvalidator, formgene = formgene, genespecs = False, chipsetspecs = chipsetspecs, datapointtypes = datapointtypes, DPVALIDATOR = dict(DPVALIDATOR), project_link_deny = True))

@login_required
@admin_required
@require_http_methods(['POST'])
def chipset_specifications_remove(request, project_pk):
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # window.location.pathname
    if request.POST.get('return_page') == reverse('project_view', kwargs = dict(project_pk = project_pk)):
        chipsetspec_data_level = request.POST.get('custom_chipsetspec_data_level')
        chipsetspec_data_pk = request.POST.get('custom_chipsetspec_data_pk')
        try:
            if chipsetspec_data_level == 'chipsetspec':
                chipset_pk = chipsetspec_data_pk
                # ChipsetSpecification.objects.get(pk = chipset_pk, project_id = project_pk).delete()
                [c.delete() for c in ChipsetSpecification.objects.get(pk = chipset_pk, project_id = project_pk)]
            elif chipsetspec_data_level == 'gene':
                chipset_pk, gene_pk = chipsetspec_data_pk.split(',')
                chipsetspec = ChipsetSpecification.objects.get(pk = chipset_pk, project_id = project_pk)
                chipsetspec.genes.remove(gene_pk)
            else:
                messages.error(request, 'Unknown request')
                return return_page
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'Chipset specification has already been linked with results')
            messages.error(request, f'Error in deleting chipset specifications associated with selected {chipsetspec_data_level}')
        return return_page
    else:
        pass
    return HttpResponse("HI")

@login_required
@admin_required
def patient_specifications_sort(request, project_pk):
    return_page = HttpResponseRedirect(reverse('patient_specifications_sort', kwargs = dict(project_pk = project_pk)))
    if request.method == 'POST':
        patientdpt_pks = request.POST.get('patientdpt_pks')
        if not patientdpt_pks:
            messages.info(request, 'No changes')
            return return_page
        patientdpt_pks = patientdpt_pks.split(',')
        try:
            for patientdpt_index, patientdpt_pk in enumerate(patientdpt_pks):
                patientdpt = PatientDPTs.objects.get(pk = patientdpt_pk)
                patientdpt.priority = patientdpt_index
                patientdpt.save()
            return return_page
        except:
            messages.error(request, 'Error in sorting datapointtypes')
            return return_page
    projects = Project.objects.order_by('-pk')
    patientspec = PatientSpecification.objects.get(project_id = project_pk)
    return render(request, 'ui_new/admin/patient_specifications/patient_specifications_sort.html', dict(projects = projects, project_pk = project_pk, patientspec = patientspec, project_link_deny = True))

@login_required
@admin_required
def patient_specifications_add(request, project_pk):
    return_page = HttpResponseRedirect(reverse('patient_specifications_add', kwargs = dict(project_pk = project_pk)))
    if request.method == "POST":
        patient_specs = json.loads(request.POST.get("patient_specs"))
        if str(project_pk) != patient_specs['project_pk']:
            messages.error(request, 'Invalid form submitted')
            return return_page
        try:
            patientspec = PatientSpecification.objects.get(project_id = project_pk)
            # check if patient exist
            projectids = patientspec.project.projectid_project.all()
            if patient_specs['dpts']:
                for dpt_pk, dpt_value in patient_specs['dpts_dict'].items():
                    patientdpts = PatientDPTs(patientspec = patientspec, datapointtype_id = dpt_pk, mandatory = dpt_value['mandatory'], default = dpt_value['default'])
                    patientdpts.save()
                    if not projectids:
                        response = fn_checkdpts(patientdpts, strict = False)
                        if not response['ok']:
                            patientdpts.delete()
                            messages.error(request, response['message'])
                            return return_page
                    else:
                        response = fn_checkdpts(patientdpts, strict = True)
                        if not response['ok']:
                            patientdpts.delete()
                            messages.error(request, response['message'])
                            return return_page
                        ivalue = patientdpts.default
                        if ivalue:
                            # check validators
                            response = fn_checkvalidator(ivalue, patientdpts.datapointtype)
                            if not response['ok']:
                                messages.error(request, response['message'])
                                return return_page
                        datapoint_pks = []
                        try:
                            for projectid in projectids:
                                datapoint = PatientDatapoint(patientdpts = patientdpts, value = ivalue)
                                datapoint.save()
                                datapoint_pks.append(datapoint.pk)
                                projectid.patientinfo.datapoints.add(datapoint)
                        except Exception as e:
                            messages.error(request, e)
                            # PatientDatapoint.objects.filter(pk__in = datapoint_pks).delete()
                            [p.delete() for p in PatientDatapoint.objects.filter(pk__in = datapoint_pks)]
                            return return_page
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in creating patient specifications')
            return return_page
        messages.success(request, 'Success')
        return HttpResponseRedirect(reverse('project_view', kwargs = dict(project_pk = project_pk)))
    formproject = ProjectAddForm()
    formdatatype = DatapointTypeAddForm()
    formvalidator = DatapointValidatorAddForm() 
    projects = Project.objects.order_by('-pk')
    # genespecs = list(Specification.objects.filter(project_id = project_pk).values('gene_id', 'method_id', 'status', 'method__name', 'gene__name'))
    patientspec = PatientSpecification.objects.get(project_id = project_pk)
    dpts = list(DatapointType.objects.exclude(name = content['default_none']).order_by('name').values('pk', 'name', 'options', 'helptext', 'rcmd_methods__id'))
    datapointtypes = fn_aggregate_rcmd_ids(dpts)
    # return HttpResponse(datapointtypes)
    #
    return render(request, 'ui_new/admin/patient_specifications/patient_specifications_add.html', dict(projects = projects, project_pk = project_pk, formproject = formproject, formdatatype = formdatatype, formvalidator = formvalidator, datapointtypes = datapointtypes, DPVALIDATOR = dict(DPVALIDATOR), patientspec = patientspec, project_link_deny = True))

@login_required
@admin_required
def sample_specifications_sort(request, project_pk):
    return_page = HttpResponseRedirect(reverse('sample_specifications_sort', kwargs = dict(project_pk = project_pk)))
    if request.method == 'POST':
        sampledpt_pks = request.POST.get('sampledpt_pks')
        if not sampledpt_pks:
            messages.info(request, 'No changes')
            return return_page
        sampledpt_pks = sampledpt_pks.split(',')
        try:
            for sampledpt_index, sampledpt_pk in enumerate(sampledpt_pks):
                sampledpt = SampleDPTs.objects.get(pk = sampledpt_pk)
                sampledpt.priority = sampledpt_index
                sampledpt.save()
            return return_page
        except:
            messages.error(request, 'Error in sorting datapointtypes')
            return return_page
    projects = Project.objects.order_by('-pk')
    samplespec = SampleSpecification.objects.get(project_id = project_pk)
    return render(request, 'ui_new/admin/sample_specifications/sample_specifications_sort.html', dict(projects = projects, project_pk = project_pk, samplespec = samplespec, project_link_deny = True))

@login_required
@admin_required
def sample_specifications_add(request, project_pk):
    return_page = HttpResponseRedirect(reverse('sample_specifications_add', kwargs = dict(project_pk = project_pk)))
    if request.method == "POST":
        sample_specs = json.loads(request.POST.get("sample_specs"))
        if str(project_pk) != sample_specs['project_pk']:
            messages.error(request, 'Invalid form submitted')
            return return_page
        try:
            samplespec = SampleSpecification.objects.get(project_id = project_pk)
            # check if sample exist
            projectids = samplespec.project.projectid_project.all()
            sample_exist = any([projectid.sample_projectid.exists() for projectid in projectids])
            if sample_specs['dpts']:
                for dpt_pk, dpt_value in sample_specs['dpts_dict'].items():
                    sampledpts = SampleDPTs(samplespec = samplespec, datapointtype_id = dpt_pk, mandatory = dpt_value['mandatory'], default = dpt_value['default'])
                    sampledpts.save()
                    if not sample_exist:
                        response = fn_checkdpts(sampledpts, strict = False)
                        if not response['ok']:
                            sampledpts.delete()
                            messages.error(request, response['message'])
                            return return_page
                    else:
                        response = fn_checkdpts(sampledpts, strict = True)
                        if not response['ok']:
                            sampledpts.delete()
                            messages.error(request, response['message'])
                            return return_page
                        ivalue = sampledpts.default
                        if ivalue:
                            # check validators
                            response = fn_checkvalidator(ivalue, sampledpts.datapointtype)
                            if not response['ok']:
                                messages.error(request, response['message'])
                                return return_page
                        datapoint_pks = []
                        try:
                            projectids_pks = list(projectids.values_list('pk', flat = True))
                            for sample in Sample.objects.filter(projectid_id__in = projectids_pks):
                                datapoint = SampleDatapoint(sampledpts = sampledpts, value = ivalue)
                                datapoint.save()
                                datapoint_pks.append(datapoint.pk)
                                sample.sampleinfo.datapoints.add(datapoint)
                        except Exception as e:
                            messages.error(request, e)
                            # SampleDatapoint.objects.filter(pk__in = datapoint_pks).delete()
                            [s.delete() for s in SampleDatapoint.objects.filter(pk__in = datapoint_pks)]
                            return return_page
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in creating sample specifications')
            return return_page
        messages.success(request, 'Success')
        return HttpResponseRedirect(reverse('project_view', kwargs = dict(project_pk = project_pk)))
    formproject = ProjectAddForm()
    formdatatype = DatapointTypeAddForm()
    formvalidator = DatapointValidatorAddForm() 
    projects = Project.objects.order_by('-pk')
    # genespecs = list(Specification.objects.filter(project_id = project_pk).values('gene_id', 'method_id', 'status', 'method__name', 'gene__name'))
    samplespec = SampleSpecification.objects.get(project_id = project_pk)
    dpts = list(DatapointType.objects.exclude(name = content['default_none']).order_by('name').values('pk', 'name', 'options', 'helptext', 'rcmd_methods__id'))
    datapointtypes = fn_aggregate_rcmd_ids(dpts)
    # return HttpResponse(datapointtypes)
    #
    return render(request, 'ui_new/admin/sample_specifications/sample_specifications_add.html', dict(projects = projects, project_pk = project_pk, formproject = formproject, formdatatype = formdatatype, formvalidator = formvalidator, datapointtypes = datapointtypes, DPVALIDATOR = dict(DPVALIDATOR), samplespec = samplespec, project_link_deny = True))