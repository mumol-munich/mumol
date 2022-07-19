from django import template
from django.urls import reverse
from django.utils.html import format_html

import json

from ..config import content

register = template.Library()


def string_to_dict(string):
    mydict = dict()
    for s in string.split(','):
        key, value = s.split('=')
        mydict[key] = value
    return mydict

@register.filter(name='string_to_list')
def string_to_list(string):
    return string.split(',')

@register.filter(name='select_objects')
def select_objects(objects, string):
    mydict = string_to_dict(string)
    if not mydict or not objects:
        return None
    return objects.filter(**mydict)

# @register.filter(name = 'filter_patients_by_project_pk')
# def filter_patients_by_project_pk(objects, string):
#     project_pks, exclude = string.split('.')
#     project_pks = project_pks.split(',')
#     if exclude == 'true':
#         return objects.exclude(project_id__in = project_pks)
#     else:
#         return objects.filter(project_id__in = project_pks)

# @register.filter(name = 'project_id_links')
# def project_id_links(objects, string):
#     htmlstr = ''
#     for o in objects:
#         if htmlstr != '':
#             htmlstr += ','
#         if string == 'projectid':
#             htmlstr += o.projectid
#         elif string == 'pk':
#             htmlstr += str(o.pk)
#     return htmlstr

@register.filter(name = 'patient_projectid_pk')
def patient_projectid_pk(projectids, project_pk):
    try:
        return projectids.get(project_id = project_pk).pk
    except:
        return ''

@register.filter(name = 'patient_projectid_link')
def patient_projectid_link(projectids, project_pk):
    htmlstr = ''
    try:
        projectid = projectids.get(project_id = project_pk)
        htmlstr += '<a href="' + reverse('patient_view_user', kwargs = dict(projectid_pk = projectid.pk)) + '" class="btn-link text-primary"><u>' + projectid.projectid + '</u></a>'
    except:
        htmlstr += ''
    return format_html(htmlstr)

@register.filter(name = 'patient_projectid_link_exclude')
def patient_projectid_link_exclude(projectids, project_pk):
    # htmlstr = ''
    # for projectid in projectids.exclude(project_id = project_pk):
    #     htmlstr += '<a href="' + reverse('patient_view_user', kwargs = dict(projectid_pk = projectid.pk)) + '" class="btn-link">' + projectid.projectid + '</a><br>'
    # return format_html(htmlstr)
    return projectids.exclude(project_id = project_pk)

@register.filter(name = 'arraycount')
def arraycount(array):
    return len(json.loads(array))

@register.filter(name = 'gene_confdpt_pks')
def gene_confdpt_pks(confdpts, genes):
    mylist = []
    for gene in genes:            
        for confdpt in confdpts:
            mylist.append(dict(gene_pk = gene.pk, confdpt_pk = confdpt['pk']))
    return json.dumps(mylist)

@register.filter(name = 'gene_specification_link')
def gene_specification_link(specification):
    htmlstr = ''
    # htmlstr += f'<a href="#" class="btn-link">{specification.method}</a>'
    htmlstr += '<a href="' + reverse('admin_attributes_method', kwargs = dict(method_pk = specification.method.pk)) + '" class="btn-link text-primary"><u>' + specification.method.name + '</u></a>'
    htmlstr += ' &gt; <a href="' + reverse('admin_attributes_gene', kwargs = dict(gene_pk = specification.gene.pk)) + '" class="btn-link text-primary"><u>' + specification.gene.name + '</u></a>'
    htmlstr += ' &gt; <a href="' + reverse('admin_attributes_gene_specification', kwargs = dict(genespec_pk = specification.pk)) + '" class="btn-link text-primary"><u>' + specification.status + '</u></a>'
    return format_html(htmlstr)

@register.filter(name = 'get_project_name')
def get_project_name(projects, project_pk):
    htmlstr = ''
    try:
        htmlstr = projects.get(pk = project_pk).name
    except:
        pass
    return format_html(htmlstr)

@register.filter(name = 'set_icons')
def set_icons(string):
    htmlstr = string
    if string == 'project':
        htmlstr = '<i class="fas fa-cube mx-1"></i>'
    elif string == 'method':
        htmlstr = '<i class="fas fa-box ic-w mx-1"></i>'
    elif string == 'gene':
        htmlstr = '<i class="fas fa-dna ic-w mx-1"></i>'
    elif string == 'chipset':
        htmlstr = '<i class="fas fa-table ic-w mx-1"></i>'
    elif string == 'status':
        htmlstr = ''
    elif string == 'patients':
        htmlstr = '<i class="fas fa-users mx-1"></i>'
    elif string == 'samples':
        htmlstr = '<i class="fas fa-vials mx-1"></i>'
    elif string == 'geneanalyses':
        htmlstr = '<i class="fas fa-flask mx-1"></i>'
    elif string == 'chipsetanalyses':
        htmlstr = '<i class="fas fa-chess-board mx-1"></i>'
    elif string == 'geneanalysis':
        htmlstr = ''
    elif string == 'chipsetanalysis':
        htmlstr = ''
    elif string == 'patient':
        htmlstr = '<i class="fas fa-user mx-1"></i>'
    elif string == 'sample':
        htmlstr = '<i class="fas fa-vial mx-1"></i>'
    elif string == 'specification':
        htmlstr = '<i class="fas fa-scroll mx-1"></i>'
    elif string == 'datapoint':
        htmlstr = '<i class="fas fa-caret-right mx-1"></i>'
    return format_html(htmlstr)

@register.filter(name='method_info')
def select_objects(method, string):
    if string == 'projects':
        return method.specification_method.values('project__name').distinct().count()
    elif string == 'genes':
        return method.specification_method.values('gene__name').distinct().count()
    else:
        return False

@register.filter(name='gene_info')
def select_objects(gene, string):
    if string == 'projects':
        return gene.specification_gene.values('project__name').distinct().count()
    elif string == 'methods':
        return gene.specification_gene.values('method__name').distinct().count()
    else:
        return False

@register.filter(name='dpt_filter')
def dpt_filter(datapoints, datapointtype_pk):
    htmlstr = '<td></td>'
    datapoint = datapoints.filter(specdpts__datapointtype_id = datapointtype_pk).first()
    if datapoint:
        htmlstr = '<td>' + datapoint.value + '</td>'
    # for datapoint in datapoints:
    #     if datapoint.get_datapointtype_id() == datapointtype_pk:
    #         htmlstr = '<td>' + datapoint.value + '</td>'
    return format_html(htmlstr)

@register.filter(name='cdpt_filter')
def cdpt_filter(datapoints, datapointtype_pk):
    htmlstr = '<td></td>'
    datapoint = datapoints.filter(confdpts__datapointtype_id = datapointtype_pk).first()
    if datapoint:
        htmlstr = '<td>' + datapoint.value + '</td>'
    # datapointtype_pk, gene_pk = genedptpks.split(',')
    # datapoint = datapoints.filter(confdpts__datapointtype_id = datapointtype_pk, gene_id = gene_pk).first()
    # if datapoint:
    #     htmlstr = '<td>' + datapoint.value + '</td>'
    return format_html(htmlstr)

@register.filter(name='dpt_exclude_none')
def dpt_exclude_none(dpts):
    if not dpts:
        return []
    return dpts.exclude(datapointtype__name = content['default_none'])

@register.filter(name='dpt_exclude_none2')
def dpt_exclude_none2(dpts):
    if not dpts:
        return []
    return dpts.exclude(name = content['default_none'])

@register.filter(name='queryset_index_value')
def queryset_index_value(objects, index):
    if objects[index]:
        return objects[index]
    else:
        return False

@register.filter(name='patientdpt_extract')
def patientdpt_extract(object, projectid_pk):
    htmlstr = ''
    datapoint = object.datapoint_patientdpts.filter(patientinfo_datapoint__projectid_id = projectid_pk).first()
    if datapoint:
        htmlstr = datapoint.value
    return htmlstr

@register.filter(name='sampledpt_extract')
def sampledpt_extract(object, projectid_pk):
    htmlstr = ''
    datapoint = object.datapoint_sampledpts.filter(sampleinfo_datapoint__sample__projectid_id = projectid_pk).first()
    if datapoint:
        htmlstr = datapoint.value
    return htmlstr

@register.filter(name='concatstring')
def concatstring(string1, string2):
    return str(string1) + str(string2)