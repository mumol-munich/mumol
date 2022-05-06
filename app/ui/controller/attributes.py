from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from ..decorators import admin_required
from ..config import content
from ..choices import DPVALIDATOR
from ..models import AnalysisMethod, DatapointValidator, DatapointType, Gene, Project, Specification, ChipsetSpecification, SpecDPTs, Datapoint, ChipsetDatapoint, ConfDPTs, PatientDPTs, SampleDPTs
from ..forms import MethodAddForm, DatapointTypeAddForm, GeneAddForm, ProjectAddForm, DatapointValidatorAddForm
from ..functions import fn_checkvalidatortype

import json

@login_required
@admin_required
def admin_attributes_datapointtypes(request):
    projects = Project.objects.order_by('-pk')
    datapointtypes = DatapointType.objects.exclude(name = content['default_none']).order_by('-pk')
    formadd = ProjectAddForm()
    formdatatype = DatapointTypeAddForm()
    formvalidator = DatapointValidatorAddForm() 
    return render(request, 'ui_new/admin/attributes/datapointtypes.html', dict(projects = projects, datapointtypes = datapointtypes, formproject = formadd, formdatatype = formdatatype, formvalidator = formvalidator, project_add_allow = True, current_page = 'datapointtypes', DPVALIDATOR = dict(DPVALIDATOR)))

@login_required
@admin_required
def admin_attributes_specifications(request):
    projects = Project.objects.order_by('-pk')
    genespecs = Specification.objects.order_by('-pk')
    chipsetspecs = ChipsetSpecification.objects.order_by('-pk')
    # patientspecs = 
    formadd = ProjectAddForm()
    return render(request, 'ui_new/admin/attributes/specifications.html', dict(projects = projects, genespecs = genespecs, chipsetspecs = chipsetspecs, formproject = formadd, project_add_allow = True, current_page = 'specifications'))

@login_required
@admin_required
def admin_attributes_gene_specification(request, genespec_pk):
    try:
        genespec = Specification.objects.get(pk = genespec_pk)
    except Exception as e:
        messages.error(request, e)
        messages.error(request, 'Error in accessing selected gene specification')
        return HttpResponseRedirect(reverse('admin_attributes_specifications'))
    projects = Project.objects.order_by('-pk')
    datapointtypes = DatapointType.objects.exclude(specdpts_datapointtype__in = genespec.specdpts_specification.all()).exclude(name = content['default_none'])
    formadd = ProjectAddForm()
    return render(request, 'ui_new/admin/attributes/gene_specification.html', dict(projects = projects, genespec = genespec, formproject = formadd, project_add_allow = True, current_page = 'gene_specification', datapointtypes = datapointtypes))

@login_required
@admin_required
def admin_attributes_chipset_specification(request, chipsetspec_pk):
    try:
        chipsetspec = ChipsetSpecification.objects.get(pk = chipsetspec_pk)
    except Exception as e:
        messages.error(request, e)
        messages.error(request, 'Error in accessing selected chipset specification')
        return HttpResponseRedirect(reverse('admin_attributes_specifications'))
    projects = Project.objects.order_by('-pk')
    datapointtypes = DatapointType.objects.exclude(confdpts_datapointtype__in = chipsetspec.confdpts_chipsetspec.all()).exclude(name = content['default_none'])
    formadd = ProjectAddForm()
    return render(request, 'ui_new/admin/attributes/chipset_specification.html', dict(projects = projects, chipsetspec = chipsetspec, formproject = formadd, project_add_allow = True, current_page = 'chipset_specification', datapointtypes = datapointtypes))

@login_required
@admin_required
def admin_attributes_genes(request):
    projects = Project.objects.order_by('-pk')
    genes = Gene.objects.order_by('name')
    formadd = ProjectAddForm()
    formgene = GeneAddForm()
    return render(request, 'ui_new/admin/attributes/genes.html', dict(projects = projects, genes = genes, formproject = formadd, formgene = formgene, project_add_allow = True, current_page = 'genes'))

@login_required
@admin_required
def admin_attributes_genes(request):
    projects = Project.objects.order_by('-pk')
    genes = Gene.objects.order_by('name')
    formadd = ProjectAddForm()
    formgene = GeneAddForm()
    return render(request, 'ui_new/admin/attributes/genes.html', dict(projects = projects, genes = genes, formproject = formadd, formgene = formgene, project_add_allow = True, current_page = 'genes'))

@login_required
@admin_required
def admin_attributes_gene(request, gene_pk):
    return_page = HttpResponseRedirect(reverse('admin_attributes_genes'))
    if request.method == "POST":
        access_type = request.POST.get('access_type')
        if access_type == 'add':
            project_pk = request.POST.get('id_name_project')
            return HttpResponseRedirect(reverse('gene_specifications_add', kwargs = dict(project_pk = project_pk)))
        elif access_type == 'remove':
            genespec_pks = request.POST.get('genespec_pks').split(',')
            try:
                # Specification.objects.filter(pk__in = genespec_pks).delete()
                [s.delete() for s in Specification.objects.filter(pk__in = genespec_pks)]
            except Exception as e:
                # messages.error(request, e)
                messages.error(request, 'One or more selected specifications is associated with results')
                return HttpResponseRedirect(reverse('admin_attributes_gene', kwargs = dict(gene_pk = gene_pk)))
        else:
            return return_page
    try:
        gene = Gene.objects.get(pk = gene_pk)
    except:
        messages.error(request, 'Error in accessing selected gene')
        return return_page
    projects = Project.objects.order_by('-pk')
    return render(request, 'ui_new/admin/attributes/gene.html', dict(projects = projects, gene = gene, current_page = 'gene'))



@login_required
@admin_required
def admin_attributes_methods(request):
    projects = Project.objects.order_by('-pk')
    methods = AnalysisMethod.objects.order_by('-pk')
    formadd = ProjectAddForm()
    formmethod = MethodAddForm()
    return render(request, 'ui_new/admin/attributes/methods.html', dict(projects = projects, methods = methods, formproject = formadd, formmethod = formmethod, project_add_allow = True, current_page = 'methods'))

@login_required
@admin_required
def admin_attributes_method(request, method_pk):
    return_page = HttpResponseRedirect(reverse('admin_attributes_methods'))
    if request.method == "POST":
        access_type = request.POST.get('access_type')
        if access_type == 'add':
            project_pk = request.POST.get('id_name_project')
            return HttpResponseRedirect(reverse('gene_specifications_add', kwargs = dict(project_pk = project_pk)))
        elif access_type == 'remove':
            genespec_pks = request.POST.get('genespec_pks').split(',')
            try:
                # Specification.objects.filter(pk__in = genespec_pks).delete()
                [s.delete() for s in Specification.objects.filter(pk__in = genespec_pks)]
            except Exception as e:
                # messages.error(request, e)
                messages.error(request, 'One or more selected specifications is associated with results')
                return HttpResponseRedirect(reverse('admin_attributes_method', kwargs = dict(method_pk = method_pk)))
        else:
            return return_page
    try:
        method = AnalysisMethod.objects.get(pk = method_pk)
    except:
        messages.error(request, 'Error in accessing selected method')
        return return_page
    projects = Project.objects.order_by('-pk')
    return render(request, 'ui_new/admin/attributes/method.html', dict(projects = projects, method = method, current_page = 'method'))


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_method_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # sending window.location.pathname
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        form = MethodAddForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Success')
        else:
            messages.error(request, form.errors)
    elif access_type == 'remove':
        method_pks = request.POST.get('method_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            methods = AnalysisMethod.objects.filter(pk__in=method_pks)
            # force_delete
            if force_delete:
                for method in methods:
                    # gene specification
                    genespecs = method.specification_method.all()
                    for genespec in genespecs:
                        # specdpts
                        specdpts = genespec.specdpts_specification.all()
                        for specdpt in specdpts:
                            datapoints = specdpt.datapoint_specdpts.all()
                            [d.delete() for d in datapoints]
                            specdpt.delete()
                        # geneanalysis
                        [g.delete() for g in genespec.geneanalysis_specification.all()]
                        genespec.delete()
            [m.delete() for m in methods]
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'Selected methods have been linked to at least one of the specifications')
    return return_page

@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_gene_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # sending window.location.pathname
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        form = GeneAddForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, 'Success')
        else:
            messages.error(request, form.errors)
    elif access_type == 'remove':
        gene_pks = request.POST.get('gene_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            genes = Gene.objects.filter(pk__in=gene_pks)
            # force_delete
            if force_delete:
                for gene in genes:
                    genespecs = gene.specification_gene.all()
                    for genespec in genespecs:
                        # specdpts
                        specdpts = genespec.specdpts_specification.all()
                        for specdpt in specdpts:
                            datapoints = specdpt.datapoint_specdpts.all()
                            [d.delete() for d in datapoints]
                            specdpt.delete()
                        # geneanalysis
                        [g.delete() for g in genespec.geneanalysis_specification.all()]
                        genespec.delete()
                    chipsetspecs = gene.chipsetspec_genes.all()
                    for chipsetspec in chipsetspecs:
                        # confdpts
                        confdpts = chipsetspec.confdpts_chipsetspec.all()
                        for confdpt in confdpts:
                            [d.delete() for d in confdpt.datapoint_confdpts.all()]
                            confdpt.delete()
                        # chipsetanalyses
                        [c.delete() for c in chipsetspec.chipsetanalysis_chipsetspec.all()]
                        chipsetspec.delete()
            [g.delete() for g in genes]
            messages.success(request, 'Success')
        except Exception as e:
            messages.error(request, e)
    return return_page

@login_required
@admin_required
@require_http_methods(['POST'])
def admin_datapoints_types_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page')) # sending window.location.pathname
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        form = DatapointTypeAddForm(request.POST or None)
        if form.is_valid():
            # new
            datapointtype = form.save(commit = False)
            if datapointtype.type == 'boolean':
                option_1, option_2 = request.POST.get('add_boolean_1'), request.POST.get('add_boolean_2')
                if not option_1 and not option_2:
                    messages.error(request, 'Boolean options not selected')
                    return return_page
                datapointtype.options = option_1 + ',' + option_2
            elif datapointtype.type == 'select' or datapointtype.type == 'multiple':
                options = request.POST.get('add_multiple_val')
                datapointtype.options = options
            datapointtype.save()
            array_list = request.POST.get('array_list')
            if array_list:
                dptvalidator_pks = []
                array_list = array_list.split(',')
                for i in array_list:
                    validator, value, errormsg = request.POST.get('validator_add_validator_' + i), request.POST.get('validator_add_value_' + i), request.POST.get('validator_add_errormsg_' + i)
                    if not (validator or value):
                        datapointtype.delete()
                        # DatapointValidator.objects.filter(pk__in = dptvalidator_pks).delete()
                        [d.delete() for d in DatapointValidator.objects.filter(pk__in = dptvalidator_pks)]
                        messages.error(request, 'Validator is not defined properly')
                        return return_page
                    # check validator types
                    response = fn_checkvalidatortype(datapointtype, validator, value)
                    if not response['ok']:
                        datapointtype.delete()
                        # DatapointValidator.objects.filter(pk__in = dptvalidator_pks).delete()
                        [d.delete() for d in DatapointValidator.objects.filter(pk__in = dptvalidator_pks)]
                        messages.error(request, response['message'])
                        return return_page
                    datapointvalidator = DatapointValidator(validator = validator, value = value, errormessage = errormsg)
                    datapointvalidator.save()
                    dptvalidator_pks.append(datapointvalidator.pk)
                    datapointtype.validators.add(datapointvalidator)
                datapointtype.save()
            messages.success(request, 'Success')
        else:
            messages.error(request, form.errors)
    elif access_type == 'remove':
        datapointtype_pks = request.POST.get('datapointtype_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            datapointtypes = DatapointType.objects.exclude(name = content['default_none']).filter(pk__in=datapointtype_pks)
            # force_delete
            if force_delete:
                for datapointtype in datapointtypes:
                    # patientdpts
                    patientdpts = datapointtype.patientdpts_datapointtype.all()
                    for patientdpt in patientdpts:
                        [d.delete() for d in patientdpt.datapoint_patientdpts.all()]
                        patientdpt.delete()
                    # sampledpts
                    sampledpts = datapointtype.sampledpts_datapointtype.all()
                    for sampledpt in sampledpts:
                        [d.delete() for d in sampledpt.datapoint_sampledpts.all()]
                        sampledpt.delete()
                    # specdpts
                    specdpts = datapointtype.specdpts_datapointtype.all()
                    for specdpt in specdpts:
                        datapoints = specdpt.datapoint_specdpts.all()
                        [d.delete() for d in datapoints]
                        specdpt.delete()
                    # confdpts
                    confdpts = datapointtype.confdpts_datapointtype.all()
                    for confdpt in confdpts:
                        [d.delete() for d in confdpt.datapoint_confdpts.all()]
                        confdpt.delete()
            [d.delete() for d in DatapointValidator.objects.filter(datapointvalidator_validators__in = datapointtype_pks)]
            [d.delete() for d in datapointtypes]
            messages.success(request, 'Success')
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'At least one of the datapoint type has been used in the results')
    return return_page

@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_genespec_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        project_pk = request.POST.get('id_name_project')
        return HttpResponseRedirect(reverse('gene_specifications_add', kwargs = dict(project_pk = project_pk)))
    elif access_type == 'remove':
        genespec_pks = request.POST.get('genespec_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            # Specification.objects.filter(pk__in = genespec_pks).delete()
            genespecs = Specification.objects.filter(pk__in = genespec_pks)
            # force_delete
            if force_delete:
                for genespec in genespecs:
                    # specdpts
                    specdpts = genespec.specdpts_specification.all()
                    for specdpt in specdpts:
                        datapoints = specdpt.datapoint_specdpts.all()
                        [d.delete() for d in datapoints]
                        specdpt.delete()
                    # geneanalysis
                    [g.delete() for g in genespec.geneanalysis_specification.all()]
            [g.delete() for g in genespecs]
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'One or more selected specifications is associated with results')
        return return_page
    else:
        messages.error(request, 'Unknown route')
        return return_page

@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_chipsetspec_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        project_pk = request.POST.get('id_name_project2')
        return HttpResponseRedirect(reverse('chipset_specifications_add', kwargs = dict(project_pk = project_pk)))
    elif access_type == 'remove':
        chipsetspec_pks = request.POST.get('chipsetspec_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            chipsetspecs = ChipsetSpecification.objects.filter(pk__in = chipsetspec_pks)
            # force_delete
            if force_delete:
                for chipsetspec in chipsetspecs:
                    # confdpts
                    confdpts = chipsetspec.confdpts_chipsetspec.all()
                    for confdpt in confdpts:
                        [d.delete() for d in confdpt.datapoint_confdpts.all()]
                        confdpt.delete()
                    # chipsetanalyses
                    [c.delete() for c in chipsetspec.chipsetanalysis_chipsetspec.all()]
            [c.delete() for c in chipsetspecs]
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'One or more selected specifications is associated with results')
        return return_page
    else:
        messages.error(request, 'Unknown route')
        return return_page

@login_required
@admin_required
def admin_attributes_specdpt_sort(request, genespec_pk):
    return_page = HttpResponseRedirect(reverse('admin_attributes_specdpt_sort', kwargs = dict(genespec_pk = genespec_pk)))
    if request.method == 'POST':
        specdpt_pks = request.POST.get('specdpt_pks')
        if not specdpt_pks:
            messages.info(request, 'No changes')
            return return_page
        specdpt_pks = specdpt_pks.split(',')
        try:
            for specdpt_index, specdpt_pk in enumerate(specdpt_pks):
                specdpt = SpecDPTs.objects.get(pk = specdpt_pk)
                specdpt.priority = specdpt_index
                specdpt.save()
            return return_page
        except:
            messages.error(request, 'Error in sorting datapointtypes')
            return return_page
    projects = Project.objects.order_by('-pk')
    genespec = Specification.objects.get(pk = genespec_pk)
    return render(request, 'ui_new/admin/gene_specifications/gene_specifications_sort.html', dict(projects = projects, project_pk = genespec.project.pk, genespec = genespec, project_link_deny = True))

@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_specdpt_add_remove(request, genespec_pk):
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    access_type = request.POST.get('access_type')
    try:
        genespec = Specification.objects.get(pk = genespec_pk)
    except:
        messages.error(request, 'Error in accessing requested gene specification')
        return HttpResponseRedirect(reverse('admin_attributes_specifications'))
    if access_type == 'add':
        id_datapointtype, id_mandatory, id_default = request.POST.get('id_datapointtype'), request.POST.get('id_mandatory'), request.POST.get('id_default')
        if not id_mandatory:
            id_mandatory = False
        else:
            id_mandatory = True
        try:
            specdpts = SpecDPTs(specification_id = genespec.pk, datapointtype_id = id_datapointtype, mandatory = id_mandatory, default = id_default)
            specdpts.save()
            messages.success(request, 'Success')
            # creating datapoint for gene analysis for all results
            datapoint_pks = []
            try:
                for geneanalysis in genespec.geneanalysis_specification.all():
                    datapoint = Datapoint(specdpts_id = specdpts.pk, value = specdpts.default)
                    datapoint.save()
                    datapoint_pks.append(datapoint.pk)
                    geneanalysis.datapoints.add(datapoint)
                    geneanalysis.save()
            except:
                messages.error(request, 'Error in creating datapoints')
                # Datapoint.objects.filter(pk__in = datapoint_pks).delete()
                [d.delete() for d in Datapoint.objects.filter(pk__in = datapoint_pks)]
                return return_page
        except Exception as e:
            messages.error(request, 'Error in creating specification datapoint type')
        return return_page
    elif access_type == 'remove':
        specdpt_pks = request.POST.get('specdpt_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            specdpts = SpecDPTs.objects.filter(pk__in = specdpt_pks)
            # force_delete
            if force_delete:
                for specdpt in specdpts:
                    datapoints = specdpt.datapoint_specdpts.all()
                    [d.delete() for d in datapoints]
            [s.delete() for s in specdpts]
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'One or more selected specifications is associated with results')
        return return_page
    elif access_type == 'edit':
        id_specdpt2, id_mandatory2, id_default2 = request.POST.get('id_specdpt2'), request.POST.get('id_mandatory2'), request.POST.get('id_default2')
        try:
            specdpts = genespec.specdpts_specification.get(pk = id_specdpt2)
        except:
            messages.error(request, 'Error in accessing selected specification datapoint type')
            return return_page
        if not id_mandatory2:
            id_mandatory2 = False
        else:
            id_mandatory2 = True
        specdpts.mandatory = id_mandatory2
        specdpts.default = id_default2
        specdpts.save()
        messages.success(request, 'Success')
        return return_page
    else:
        messages.error(request, 'Unknown route')
        return return_page

@login_required
@admin_required
def admin_attributes_confdpt_sort(request, chipsetspec_pk):
    return_page = HttpResponseRedirect(reverse('admin_attributes_confdpt_sort', kwargs = dict(chipsetspec_pk = chipsetspec_pk)))
    if request.method == 'POST':
        confdpt_pks = request.POST.get('confdpt_pks')
        if not confdpt_pks:
            messages.info(request, 'No changes')
            return return_page
        confdpt_pks = confdpt_pks.split(',')
        try:
            for confdpt_index, confdpt_pk in enumerate(confdpt_pks):
                confdpt = SpecDPTs.objects.get(pk = confdpt_pk)
                confdpt.priority = confdpt_index
                confdpt.save()
            return return_page
        except:
            messages.error(request, 'Error in sorting datapointtypes')
            return return_page
    projects = Project.objects.order_by('-pk')
    chipsetspec = ChipsetSpecification.objects.get(pk = chipsetspec_pk)
    return render(request, 'ui_new/admin/chipset_specifications/chipset_specifications_sort.html', dict(projects = projects, project_pk = chipsetspec.project.pk, chipsetspec = chipsetspec, project_link_deny = True))

@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_confdpt_add_remove(request, chipsetspec_pk):
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    access_type = request.POST.get('access_type')
    try:
        chipsetspec = ChipsetSpecification.objects.get(pk = chipsetspec_pk)
    except:
        messages.error(request, 'Error in accessing requested chipset specification')
        return HttpResponseRedirect(reverse('admin_attributes_specifications'))
    if access_type == 'add':
        id_datapointtype, id_mandatory, id_default = request.POST.get('id_datapointtype'), request.POST.get('id_mandatory'), request.POST.get('id_default')
        if not id_mandatory:
            id_mandatory = False
        else:
            id_mandatory = True
        try:
            confdpts = ConfDPTs(chipsetspec_id = chipsetspec.pk, datapointtype_id = id_datapointtype, mandatory = id_mandatory, default = id_default)
            confdpts.save()
            messages.success(request, 'Success')
            # creating datapoint for gene analysis for all results
            datapoint_pks = []
            try:
                for chipsetanalysis in chipsetspec.chipsetanalysis_chipsetspec.all():
                    for gene in chipsetspec.genes.all():
                        datapoint = ChipsetDatapoint(gene_id = gene.pk, confdpts_id = confdpts.pk, value = confdpts.default)
                        datapoint.save()
                        datapoint_pks.append(datapoint.pk)
                        chipsetanalysis.datapoints.add(datapoint)
                        chipsetanalysis.save()
            except:
                messages.error(request, 'Error in creating datapoints')
                # ChipsetDatapoint.objects.filter(pk__in = datapoint_pks).delete()
                [c.delete() for c in ChipsetDatapoint.objects.filter(pk__in = datapoint_pks)]
                return return_page
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in creating specification datapoint type')
        return return_page
    elif access_type == 'remove':
        confdpt_pks = request.POST.get('confdpt_pks').split(',')
        force_delete = request.POST.get('force_delete')
        if chipsetspec.confdpts_chipsetspec.count() - len(confdpt_pks) <= 0:
            messages.error(request, 'Chipset Specification should have at least one datapoint type present in it')
            messages.warning(request, 'Please delete the whole chipset instead')
            return return_page
        try:
            confdpts = ConfDPTs.objects.filter(pk__in = confdpt_pks)
            # force_delete
            if force_delete:
                for confdpt in confdpts:
                    [d.delete() for d in confdpt.datapoint_confdpts.all()]
            [c.delete() for c in confdpts]
            messages.success(request, 'Success')
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'One or more selected specifications is associated with results')
        return return_page
    elif access_type == 'edit':
        id_confdpt2, id_mandatory2, id_default2 = request.POST.get('id_confdpt2'), request.POST.get('id_mandatory2'), request.POST.get('id_default2')
        try:
            confdpts = chipsetspec.confdpts_chipsetspec.get(pk = id_confdpt2)
        except Exception as e:
            messages.error(request, e)
            messages.error(request, 'Error in accessing selected specification datapoint type')
            return return_page
        if not id_mandatory2:
            id_mandatory2 = False
        else:
            id_mandatory2 = True
        confdpts.mandatory = id_mandatory2
        confdpts.default = id_default2
        confdpts.save()
        messages.success(request, 'Success')
        return return_page
    else:
        messages.error(request, 'Unknown route')
        return return_page


@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_patientspec_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        project_pk = request.POST.get('id_name_project')
        return HttpResponseRedirect(reverse('patient_specifications_add', kwargs = dict(project_pk = project_pk)))
    elif access_type == 'sort':
        project_pk = request.POST.get('id_name_project')
        return HttpResponseRedirect(reverse('patient_specifications_sort', kwargs = dict(project_pk = project_pk)))
    elif access_type == 'remove':
        patientdpt_pks = request.POST.get('patientdpt_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            patientdpts = PatientDPTs.objects.filter(pk__in = patientdpt_pks)
            # force_delete
            if force_delete:
                for patientdpt in patientdpts:
                    [d.delete() for d in patientdpt.datapoint_patientdpts.all()]
            [p.delete() for p in patientdpts]
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'One or more selected specifications is associated with results')
        return return_page
    else:
        messages.error(request, 'Unknown route')
        return return_page

@login_required
@admin_required
@require_http_methods(['POST'])
def admin_attributes_samplespec_add_remove(request):
    return_page = HttpResponseRedirect(request.POST.get('return_page'))
    access_type = request.POST.get('access_type')
    if access_type == 'add':
        project_pk = request.POST.get('id_name_project')
        return HttpResponseRedirect(reverse('sample_specifications_add', kwargs = dict(project_pk = project_pk)))
    if access_type == 'sort':
        project_pk = request.POST.get('id_name_project')
        return HttpResponseRedirect(reverse('sample_specifications_sort', kwargs = dict(project_pk = project_pk)))
    elif access_type == 'remove':
        sampledpt_pks = request.POST.get('sampledpt_pks').split(',')
        force_delete = request.POST.get('force_delete')
        try:
            sampledpts = SampleDPTs.objects.filter(pk__in = sampledpt_pks)
            # force_delete
            if force_delete:
                for sampledpt in sampledpts:
                    [d.delete() for d in sampledpt.datapoint_sampledpts.all()]
            [s.delete() for s in sampledpts]
            messages.success(request, 'Success')
        except Exception as e:
            # messages.error(request, e)
            messages.error(request, 'One or more selected specifications is associated with results')
        return return_page
    else:
        messages.error(request, 'Unknown route')
        return return_page