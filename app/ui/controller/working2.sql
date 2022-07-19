select projectQuery.projectName, 
patientQuery.projectid, patientQuery.firstname, patientQuery.lastname, patientQuery.dateofbirth, patientQuery.patientDatapointType, patientQuery.patientDatapoint, 
sampleQuery.dateofreceipt, sampleQuery.visit, sampleQuery.sampleDatapointType, sampleQuery.sampleDatapoint, rowQuery.chipset, rowQuery.manufacturer, rowQuery.version, rowQuery.gene, rowQuery.datapointType, rowQuery.datapoint, rowQuery.datapointsrow_id
from (
    select distinct ui_project.id as project_id, ui_project.name as projectName
    from ui_project
    left join ui_project_users on ui_project_users.project_id = ui_project.id
    left join auth_user on auth_user.id = ui_project_users.user_id
    left join ui_profile on ui_profile.user_id = auth_user.id
    -- where auth_user.username = "testuser01"
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
    select ui_chipsetdatapointsrow.id as datapointsrow_id, ui_chipsetanalysis.sample_id as sample_id, ui_chipsetspecification.name as chipset, ui_chipsetspecification.manufacturer, ui_chipsetspecification.version, 
    ui_gene.name as gene,
    group_concat(ui_datapointtype.name, '|') as datapointType,
    group_concat(ui_chipsetdatapoint.value, '|') as datapoint
    from ui_chipsetdatapointsrow
    left join ui_gene on ui_gene.id = ui_chipsetdatapointsrow.gene_id
    left join ui_chipsetanalysis_datapointsrows on ui_chipsetanalysis_datapointsrows.chipsetdatapointsrow_id = ui_chipsetdatapointsrow.id
    left join ui_chipsetanalysis on ui_chipsetanalysis.id = ui_chipsetanalysis_datapointsrows.chipsetanalysis_id
    left join ui_chipsetspecification on ui_chipsetspecification.id = ui_chipsetanalysis.chipsetspec_id
    left join ui_chipsetdatapointsrow_datapoints on ui_chipsetdatapointsrow_datapoints.chipsetdatapointsrow_id = ui_chipsetdatapointsrow.id
    left join ui_chipsetdatapoint on ui_chipsetdatapoint.id = ui_chipsetdatapointsrow_datapoints.chipsetdatapoint_id
    left join ui_confdpts on ui_confdpts.id = ui_chipsetdatapoint.confdpts_id
    left join ui_datapointtype on ui_datapointtype.id = ui_confdpts.datapointtype_id
    group by ui_chipsetdatapointsrow.id
) rowQuery on rowQuery.sample_id = sampleQuery.sample_id
limit 5
;