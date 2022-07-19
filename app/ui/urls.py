from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    # index
    path('', views.index, name = 'index'),

    # registration
    path('accounts/registration', views.registration, name='registration'),
    path('accounts/login', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),

    # user
    path('library/queries/gene', views.queries_gene_user, name = 'queries_gene_user'),
    path('library/queries/chipset', views.queries_chipset_user, name = 'queries_chipset_user'),

    path('library/projects2', views.projects_view_user2, name='projects_view_user2'),
    path('library/projects', views.projects_view_user, name='projects_view_user'),
    path('library/projects/<int:project_pk>', views.project_view_user, name='project_view_user'),
    path('library/projects/<int:project_pk>/samples', views.samples_view_user, name = 'samples_view_user'),
    path('library/projects/<int:project_pk>/samples/add_remove', views.samples_overview_add_remove, name = 'samples_overview_add_remove'),


    # patients
    path('library/projects/<int:project_pk>/patients', views.patients_view_user, name='patients_view_user'),
    path('library/projects/<int:project_pk>/patients/add_remove', views.patients_add_remove, name='patients_add_remove'),

    path('library/projectids/<int:projectid_pk>', views.patient_view_user, name='patient_view_user'),

    # samples
    path('library/samples/<int:sample_pk>', views.sample_view_user, name='sample_view_user'),
    path('library/samples/add_remove', views.samples_add_remove, name='samples_add_remove'),

    # analysis
    # path('library/samples/<int:sample_pk>/analysis/genes/add', views.gene_analysis_add, name = 'gene_analysis_add'),
    # path('library/samples/<int:sample_pk>/analysis/chipsets/add', views.chipset_analysis_add, name = 'chipset_analysis_add'),

    # analysis new
    path('library/projects/<int:project_pk>/analysis/genes', views.analysis_genes_view, name = 'analysis_genes_view'),
    path('library/samples/<int:sample_pk>/analysis/genes/add_remove', views.analysis_genes_add_remove, name = 'analysis_genes_add_remove'),
    path('library/projects/<int:project_pk>/analysis/genes/remove', views.analysis_genes_overview_remove, name = 'analysis_genes_overview_remove'),


    path('library/samples/<int:project_pk>/analysis/chipsets', views.analysis_chipsets_view, name = 'analysis_chipsets_view'),
    path('library/samples/<int:sample_pk>/analysis/chipsets/add_remove', views.analysis_chipsets_add_remove, name = 'analysis_chipsets_add_remove'),
    path('library/projects/<int:project_pk>/analysis/chipsets/remove', views.analysis_chipsets_overview_remove, name = 'analysis_chipsets_overview_remove'),

    path('library/samples/<int:sample_pk>/analysis/chipsets/upload_download', views.analysis_chipsets_upload_download, name = 'analysis_chipsets_upload_download'),
    




    # admin
    # projects
    path('admin/projects', views.projects_view, name='projects_view'),
    path('admin/projects/add_remove', views.projects_add_remove, name='projects_add_remove'),
    path('admin/projects/<int:project_pk>', views.project_view, name='project_view'),
    path('admin/projects/<int:project_pk>/users/add_remove', views.project_users_add_remove, name='project_users_add_remove'),

    # gene specifications
    path('admin/projects/<int:project_pk>/genes/specifications/add', views.gene_specifications_add, name='gene_specifications_add'),
    path('admin/projects/<int:project_pk>/genes/specifications/remove', views.gene_specifications_remove, name='gene_specifications_remove'),

    # chipset specifications
    path('admin/projects/<int:project_pk>/chipsets/specifications/add', views.chipset_specifications_add, name='chipset_specifications_add'),
    path('admin/projects/<int:project_pk>/chipsets/specifications/remove', views.chipset_specifications_remove, name='chipset_specifications_remove'),

    # patient specifications
    path('admin/projects/<int:project_pk>/patients/specifications/sort', views.patient_specifications_sort, name='patient_specifications_sort'),
    path('admin/projects/<int:project_pk>/patients/specifications/add', views.patient_specifications_add, name='patient_specifications_add'),
    # sample specifications
    path('admin/projects/<int:project_pk>/samples/specifications/add', views.sample_specifications_add, name='sample_specifications_add'),
    path('admin/projects/<int:project_pk>/samples/specifications/sort', views.sample_specifications_sort, name='sample_specifications_sort'),

    # attributes
    path('admin/attributes/methods/add_remove', views.admin_attributes_method_add_remove, name='admin_attributes_method_add_remove'),
    path('admin/attributes/genes/add_remove', views.admin_attributes_gene_add_remove, name='admin_attributes_gene_add_remove'),
    path('admin/attributes/datapoints/add_remove', views.admin_datapoints_types_add_remove, name='admin_datapoints_types_add_remove'),


    path('admin/attributes/genes/specifications/add_remove', views.admin_attributes_genespec_add_remove, name = 'admin_attributes_genespec_add_remove'),
    path('admin/attributes/chipsets/specifications/add_remove', views.admin_attributes_chipsetspec_add_remove, name = 'admin_attributes_chipsetspec_add_remove'),
    path('admin/attributes/patients/specifications/add_remove', views.admin_attributes_patientspec_add_remove, name = 'admin_attributes_patientspec_add_remove'),
    path('admin/attributes/samples/specifications/add_remove', views.admin_attributes_samplespec_add_remove, name = 'admin_attributes_samplespec_add_remove'),

    path('admin/attributes/methods', views.admin_attributes_methods, name = 'admin_attributes_methods'),
    path('admin/attributes/methods/<int:method_pk>', views.admin_attributes_method, name = 'admin_attributes_method'),

    path('admin/attributes/genes', views.admin_attributes_genes, name = 'admin_attributes_genes'),
    path('admin/attributes/genes/<int:gene_pk>', views.admin_attributes_gene, name = 'admin_attributes_gene'),

    path('admin/attributes/specifications', views.admin_attributes_specifications, name = 'admin_attributes_specifications'),
    path('admin/attributes/specifications/genes/<int:genespec_pk>', views.admin_attributes_gene_specification, name = 'admin_attributes_gene_specification'),
    path('admin/attributes/specifications/chipsets/<int:chipsetspec_pk>', views.admin_attributes_chipset_specification, name = 'admin_attributes_chipset_specification'),


    path('admin/attributes/specifications/genes/<int:genespec_pk>/specdpts/sort', views.admin_attributes_specdpt_sort, name = 'admin_attributes_specdpt_sort'),
    path('admin/attributes/specifications/genes/<int:genespec_pk>/specdpts/add_remove', views.admin_attributes_specdpt_add_remove, name = 'admin_attributes_specdpt_add_remove'),
    path('admin/attributes/specifications/chipsets/<int:chipsetspec_pk>/confdpts/sort', views.admin_attributes_confdpt_sort, name = 'admin_attributes_confdpt_sort'),
    path('admin/attributes/specifications/chipsets/<int:chipsetspec_pk>/confdpts/add_remove', views.admin_attributes_confdpt_add_remove, name = 'admin_attributes_confdpt_add_remove'),

    path('admin/attributes/datapointtypes', views.admin_attributes_datapointtypes, name = 'admin_attributes_datapointtypes'),

]