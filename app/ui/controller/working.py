from django.db import connection
import pandas as pd
from copy import deepcopy
import numpy as np

conn = connection.cursor()
conn.execute('''
select projectQuery.projectName, 
patientQuery.projectid, patientQuery.firstname, patientQuery.lastname, patientQuery.dateofbirth, patientQuery.patientDatapointType, patientQuery.patientDatapoint, 
sampleQuery.dateofreceipt, sampleQuery.visit, sampleQuery.sampleDatapointType, sampleQuery.sampleDatapoint,
rowQuery.method, rowQuery.gene, rowQuery.result, rowQuery.datapointType, rowQuery.datapoint,
rowQuery.datapointsrow_id from (
    select ui_project.id as project_id, auth_user.username, ui_project.name as projectName, ui_profile.is_admin
    from ui_project
    left join ui_project_users on ui_project_users.project_id = ui_project.id
    left join auth_user on auth_user.id = ui_project_users.user_id
    left join ui_profile on ui_profile.user_id = auth_user.id ''' + 'where auth_user.username = "testuser01"' + ''' 
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

df1 = deepcopy(df)

# new
def_cols = list(df1.columns)
req_tags = ['Patient_', 'Sample_', '']
req_cols1 = [['patientDatapointType', 'patientDatapoint'], ['sampleDatapointType', 'sampleDatapoint'], ['datapointType', 'datapoint']]
req_cols2 = [c for cs in req_cols1 for c in cs]
req_cols3 = [c for c in def_cols if c not in req_cols2]

tab1 = df1[req_cols3]

tabdf = tab1

for i, rcol in enumerate(req_cols1):
    tab2 = df1[['datapointsrow_id'] + rcol].set_index('datapointsrow_id').apply(lambda c: c.str.split('|')).reset_index()
    tab2['datapointsrow_id'] = tab2.apply(lambda d: [d['datapointsrow_id']] * len(d[rcol[0]]), axis = 1)
    tab2[rcol[1]] = tab2.apply(lambda d: d[rcol[1]][0] if len(d[rcol[1]]) == 1 else d[rcol[1]], axis = 1)
    tab2[rcol[1]] = tab2.apply(lambda x: [x[rcol[1]]] * len(x[rcol[0]]) if len(x[rcol[1]]) <= 1 else x[rcol[1]], axis = 1)
    tab2 = tab2.apply(pd.Series.explode)
    tab2[rcol[0]] = tab2.apply(lambda d: req_tags[i] + d[rcol[0]], axis = 1)
    tab2 = tab2.pivot(index = 'datapointsrow_id', columns = rcol[0], values = rcol[1])
    tabdf = pd.merge(tabdf, tab2, on = 'datapointsrow_id')

# new
