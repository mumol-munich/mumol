from django.core.validators import RegexValidator, EmailValidator, MinLengthValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator, DecimalValidator
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import DatapointType, Project
from .config import content

import uuid
from copy import deepcopy

import pandas as pd

def fn_auth_project_user(user, project_pk):
    if user.profile.is_admin or user.project_user.filter(pk = project_pk).exists():
        return dict(ok = True, message = False, return_page = False)
    return dict(ok = False, message = 'Restricted access', return_page = HttpResponseRedirect("%s?project_redirect=false" % reverse('projects_view_user')))

def fn_convert_genespec_json(genespecs):
    genespecs1 = dict()
    method_last, gene_last = False, False
    for genespec in genespecs:
        method = genespec['method__name']
        if not method_last:
            genespecs1[method] = dict(method_pk = genespec['method_id'], genes = dict())
            method_last = method
        else:
            if method_last != method:
                genespecs1[method] = dict(method_pk = genespec['method_id'], genes = dict())
                method_last = method
                method_last = method
                gene_last = False
        gene = genespec['gene__name']
        if not gene_last:
            genespecs1[method]['genes'][gene] = dict(gene_pk = genespec['gene_id'], statuslist = [])
            gene_last = gene
        else:
            if gene_last != gene:
                genespecs1[method]['genes'][gene] = dict(gene_pk = genespec['gene_id'], statuslist = [])
                gene_last = gene
        genespecs1[method]['genes'][gene]['statuslist'].append(dict(status = genespec['status'], genespec_pk = genespec['pk']))
    return dict(ok = True, genespecs = genespecs1)

def fn_checkvalidatortype(datapointtype, validator_type, validator_value):
    # check if existing
    if datapointtype.validators.filter(validator = validator_type).exists():
        return dict(ok = False, message = f'Validators added were not unique')
    allowed_validators = []
    if datapointtype.type == 'varchar':
        allowed_validators = ['regex', 'email', 'minlen', 'maxlen']
    elif datapointtype.type == 'integer':
        allowed_validators = ['regex', 'minval', 'maxval', 'minlen', 'maxlen']
    elif datapointtype.type == 'numeric':
        allowed_validators = ['regex', 'minval', 'maxval', 'minlen', 'maxlen', 'decval']
    if validator_type not in allowed_validators:
        return dict(ok = False, message = f"Selected validators are not permitted for datapointtype {datapointtype.type}")
    return dict(ok = True, message = False)

def fn_checkvalidator(ivalue, datapointtype):
    # return dict(ok = False, message = datapointtype.validators.all())
    validatortype = False
    for validator in datapointtype.validators.all():
        if validator.validator == 'regex':
            validatortype = RegexValidator(str(validator.value), validator.errormessage)
        elif validator.validator == 'email':
            validatortype = EmailValidator(str(validator.value), validator.errormessage)
        elif validator.validator == 'maxval':
            validatortype = MaxValueValidator(float(validator.value), validator.errormessage)
        elif validator.validator == 'minval':
            validatortype = MinValueValidator(float(validator.value), validator.errormessage)
        elif validator.validator == 'maxlen':
            validatortype = MaxLengthValidator(int(validator.value), validator.errormessage)
        elif validator.validator == 'minlen':
            validatortype = MinLengthValidator(int(validator.value), validator.errormessage)
        elif validator.validator == 'decval':
            validatortype = RegexValidator(float(validator.value), DecimalValidator.errormessage)
        try:
            if validator.validator in ['minval', 'maxval', 'decval']:
                ivalue = float(ivalue)
            elif validator.validator in ['regex', 'email', 'minlen', 'maxlen']:
                ivalue = str(ivalue)
            validatortype(ivalue)
        except Exception as e:
            message = datapointtype.name + ': ' + e.message
            return dict(ok = False, message = message)
    return dict(ok = True, message = False)
        

def fn_create_or_get_none_datapointtype():
    name = content['default_none']
    try:
        datapointtype = DatapointType.objects.get(name = name)
    except:
        datapointtype = DatapointType(name = name)
        datapointtype.save()
    return datapointtype.pk

def fn_generate_projectid(project_pk, projectid_val):
    if projectid_val:
        try:
            projectid = Project.objects.get(pk = project_pk, projectid_project__projectid = projectid_val)
            return dict(ok = False, message = 'Projectid already exist in this project', projectid_val = projectid_val, projectid_pk = projectid.pk)
        except:
            return dict(ok = True, message = False, projectid_val = projectid_val, projectid_pk = False)
    else:
        itmp = 0
        while itmp <= 100:
            itmp += 1
            itmpval = str(uuid.uuid4())
            # check if already exist within the project
            if not Project.objects.filter(pk = project_pk, projectid_project__projectid = itmpval).exists():
                projectid_val = itmpval
                break
        if projectid_val:
            return dict(ok = True, message = False, projectid_val = projectid_val, projectid_pk = False)
        return dict(ok = False, message = 'Error in creating projectid', projectid_val = False, projectid_pk = False)
    
def fn_aggregate_rcmd_ids(dpts):
    dpt_old = dict(pk = False)
    methodlist = []
    datapointtypes = []
    for dpt in dpts:
        if dpt['pk'] == dpt_old['pk']:
            methodlist.append(dpt['rcmd_methods__id'])
        else:
            if dpt_old['pk']:
                # update
                datapointtype = deepcopy(dpt_old)
                datapointtype['rcmd_methods__id'] = ','.join([str(m) for m in methodlist])
                datapointtypes.append(datapointtype)
                methodlist = []
                methodlist.append(dpt['rcmd_methods__id'])
            else:
                if not dpt['rcmd_methods__id'] in methodlist:
                    methodlist.append(dpt['rcmd_methods__id'])
        dpt_old = dpt
    if dpt_old['pk']:
        # update
        datapointtype = deepcopy(dpt_old)
        datapointtype['rcmd_methods__id'] = ','.join([str(m) for m in methodlist])
        datapointtypes.append(datapointtype)
        methodlist = []
        methodlist.append(dpt['rcmd_methods__id'])
    # return dpts
    # dpt_old = dict(pk = False)
    # methodlist = []
    # datapointtypes = []
    # for dpt in dpts:
    #     # print(dpt)
    #     # print(dpt_old)
    #     if dpt['pk'] != dpt_old['pk']:
    #         if dpt_old['pk']:
    #             # print(methodlist)
    #             if dpt['rcmd_methods__id']:
    #                 methodlist.append(dpt['rcmd_methods__id'])
    #             dpt_old['rcmd_methods__id'] = methodlist
    #             datapointtypes.append(dpt_old)
    #             methodlist = []
    #     if dpt['rcmd_methods__id']:
    #         methodlist.append(dpt['rcmd_methods__id'])
    #     dpt_old = dpt
    return datapointtypes

def fn_checkdpts(cdpt, strict = False):
    if cdpt.default:
        # check if default satisfies the validators
        response = fn_checkvalidator(cdpt.default, cdpt.datapointtype)
        if not response['ok']:
            return response
        options = cdpt.datapointtype.options
        if options:
            options = options.split(',')
            if cdpt.default not in options:
                return dict(ok = False, message = 'Default value not in options')
    else:
        if strict:
            return dict(ok = False, message = 'Please provide default value to set to existing entries')
    return dict(ok = True, message = False)

def fn_geneanalysis_query_df(df):
    try:
        def_cols = list(df.columns)
        req_tags = ['Patient_', 'Sample_', '']
        req_cols = [['patientDatapointType', 'patientDatapoint'], ['sampleDatapointType', 'sampleDatapoint'], ['datapointType', 'datapoint']]
        req_cols2 = [c for cs in req_cols for c in cs]
        req_cols2 = [c for c in def_cols if c not in req_cols2]
        tabdf = df[req_cols2]
        for i, rcol in enumerate(req_cols):
            tab2 = df[['datapointsrow_id'] + rcol].set_index('datapointsrow_id').apply(lambda c: c.str.split('|')).reset_index()
            tab2['datapointsrow_id'] = tab2.apply(lambda d: [d['datapointsrow_id']] * len(d[rcol[0]]), axis = 1)
            tab2[rcol[1]] = tab2.apply(lambda d: d[rcol[1]][0] if len(d[rcol[1]]) == 1 else d[rcol[1]], axis = 1)
            tab2[rcol[1]] = tab2.apply(lambda x: [x[rcol[1]]] * len(x[rcol[0]]) if len(x[rcol[1]]) <= 1 else x[rcol[1]], axis = 1)
            tab2 = tab2.apply(pd.Series.explode)
            tab2[rcol[0]] = tab2.apply(lambda d: req_tags[i] + d[rcol[0]], axis = 1)
            tab2 = tab2.pivot(index = 'datapointsrow_id', columns = rcol[0], values = rcol[1])
            tabdf = pd.merge(tabdf, tab2, on='datapointsrow_id')
        tabdf.drop('datapointsrow_id', inplace=True, axis=1)
    except Exception as e:
        # return dict(ok = False, message = e, df = False)
        return dict(ok = False, message = 'Error in processing query', df = False)
    return dict(ok = True, message = False, df = tabdf)