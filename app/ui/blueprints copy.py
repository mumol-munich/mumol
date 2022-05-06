import pandas as pd
import os, sys
from ui.functions import *
from ui.models import DatapointType, DatapointValidator, AnalysisMethod
from ui.choices import DPVALIDATOR

blueprint_file = '/opt/nazeer/datamask/test/datapoints_blueprintsv2.txt'

blueprints = pd.read_csv(blueprint_file, sep = '\t', comment = '#')

header = ['Name', 'Type', 'Helptext', 'Options', 'ValidatorType', 'ValidatorValue', 'ErrorMessage']
header_mandatory = ['Name', 'Type']

vartypes = ['numeric', 'integer', 'varchar', 'select', 'multiple', 'boolean']
vartypes1 = ['select', 'multiple', 'boolean']

dpvalidator = dict(DPVALIDATOR)

# check required columns
try:
    blueprints = blueprints[header]
except Exception:
    sys.exit(f"Columns {header} are expected")

# remove duplicate rows
blueprints = blueprints.drop_duplicates()

# check mandatory fields
for col in header_mandatory:
    if any(blueprints[col] == ''):
        sys.exit(f"Column {col} is mandatory")

# check vartype not in vartypes
if any([vartype not in vartypes for vartype in list(blueprints['Type'].unique())]):
    sys.exit(f"'Type' column should contain one of the following types: {vartypes}")

# create datapoint types
for index, row in blueprints.iterrows():
    # check if datapoint already exist
    if DatapointType.objects.filter(name = row['Name']).exists():
        # sys.exit(f"Error {row['Name']}: Datapoint already exist")
        # ignore already existing datapoints
        print(f"Warning {row['Name']}: Datapoint already exist. Skipping...")
        continue
    if row['Type'] not in vartypes1 and not any(list(pd.isna(row[['ValidatorType', 'ValidatorValue']]))):
        # check validators
        validatortypes = [validatortype.strip() for validatortype in row['ValidatorType'].split(',')]
        validatorvalues = [validatorvalue.strip() for validatorvalue in row['ValidatorValue'].split(',')]
        validatormsg = row['ErrorMessage']
        if len(validatortypes) != len(validatorvalues):
            sys.exit(f"Error {row['Name']}: Number of validator types and values does not match")
    # datapointtype
    datapointtype = DatapointType(name = row['Name'], type = row['Type'])
    if pd.isna(row['Helptext']) or row['Options'] == '':
        pass
    else:
        datapointtype.helptext = row['Helptext']
    if row['Type'] in vartypes1:
        options = row['Options']
        if pd.isna(options) or options == '':
            sys.exit(f"Error {row['Name']}: 'Options' column is mandatory for the following types: {vartypes1}")
        options = [option.strip() for option in options.split(',')]
        if row['Type'] == 'boolean':
            if len(options) != 2:
                sys.exit(f"Error {row['Name']}: Type 'boolean' should have two Options")
        datapointtype.options = ','.join(options)
    datapointtype.save()
    if row['Type'] not in vartypes1 and not any(list(pd.isna(row[['ValidatorType', 'ValidatorValue']]))):
        # validator
        dptvalidator_pks = []
        for i in range(0, len(validatortypes)):
            print(i)
            validator, value, errormsg = validatortypes[i], validatorvalues[i], validatormsg
            validator = list(dpvalidator.keys())[list(dpvalidator.values()).index(validator)]
            if not (validator or value):
                datapointtype.delete()
                DatapointValidator.objects.filter(pk__in = dptvalidator_pks).delete()
                sys.exit(f"Error {row['Name']}: Please check the validator type and value")
            response = fn_checkvalidatortype(datapointtype, validator, value)
            if not response['ok']:
                datapointtype.delete()
                DatapointValidator.objects.filter(pk__in = dptvalidator_pks).delete()
                sys.exit(f"Error {row['Name']}: {response['message']}")
            datapointvalidator = DatapointValidator(validator = validator, value = value, errormessage = validatormsg)
            datapointvalidator.save()
            dptvalidator_pks.append(datapointvalidator.pk)
            datapointtype.validators.add(datapointvalidator)

# datapointtype.save()


# ############## not done
# import pandas as pd
# import os, sys
# from ui.functions import *
# from ui.models import DatapointType, DatapointValidator
# from ui.choices import DPVALIDATOR

# blueprints_gene = pd.read_csv('/opt/nazeer/datamask/test/gene_analysis_blueprints.txt', sep = '\t', comment = '#')

# # check if datapoints exist
# dptlist = list(blueprints_gene['Datapoint'].unique())
# dptlist_missing = [dpt for dpt in dptlist if not DatapointType.objects.filter(name = dpt).exists()]
# if dptlist_missing:
#     sys.exit(f"Error: Datapoints {dptlist_missing} does not exist")

# methodlist = list(blueprints_gene['Method'].unique())

# for method in methodlist:
#     # add method
#     try:
#         analysismethod = AnalysisMethod.objects.get(name = method)
#         print(f"Analysis method {method} already exist")
#     except:
#         analysismethod = AnalysisMethod(name = method)
#         analysismethod.save()
#     for index, row in blueprints_gene[blueprints_gene.Method == method].iterrows():
#         break
#     break
###################
import pandas as pd
import os, sys
from ui.functions import *
from ui.models import DatapointType, DatapointValidator, AnalysisMethod
from ui.choices import DPVALIDATOR

blueprints_method = pd.read_csv('/opt/nazeer/datamask/test/method_blueprints.txt', sep = '\t', comment = '#')

# check if datapoints exist
dptlist = list(set([dpt.strip() for dpt in ','.join(blueprints_method['Datapoints']).split(',')]))
dptlist_missing = [dpt for dpt in dptlist if not DatapointType.objects.filter(name = dpt).exists()]

if dptlist_missing:
    sys.exit(f"The datapoints {dptlist_missing} does not exist")

# add rcmd_methods
for index, row in blueprints_method.iterrows():
    # add method
    try:
        analysismethod = AnalysisMethod.objects.get(name = row['Method'])
        print(f"Analysis method {row['Method']} already exist")
    except:
        analysismethod = AnalysisMethod(name = row['Method'])
        analysismethod.save()
    dptlist =  list(set([dpt.strip() for dpt in row['Datapoints'].split(',')]))
    for dpt in dptlist:
        datapointtype = DatapointType.objects.get(name = dpt)
        datapointtype.rcmd_methods.add(analysismethod)
