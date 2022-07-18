select projectQuery.projectName, 
patientQuery.projectid, patientQuery.firstname, patientQuery.lastname, patientQuery.dateofbirth, patientQuery.patientDatapointType, patientQuery.patientDatapoint, 
sampleQuery.dateofreceipt, sampleQuery.visit, sampleQuery.sampleDatapointType, sampleQuery.sampleDatapoint,
rowQuery.method, rowQuery.gene, rowQuery.result, rowQuery.datapointType, rowQuery.datapoint,
rowQuery.datapointsrow_id
from (
    select project_id, username, ui_project.name as projectName
    from auth_user
    left join ui_project_users on ui_project_users.user_id = auth_user.id
    left join ui_project on ui_project.id = ui_project_users.project_id
    group by auth_user.id
    having auth_user.username = "anazeer"
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
limit 10;

-- 
-- select username, id,
-- case id when 1 then 'a' else 'b'
-- end test
-- from auth_user where test = 'a';