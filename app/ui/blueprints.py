import csv
import os, sys
from ui.functions import *
from ui.models import DatapointType, DatapointValidator, AnalysisMethod
from ui.choices import DPVALIDATOR

blueprint_file = '../blueprints/datapoints_blueprintsv2.txt'

# new
header = ['Name', 'Type', 'Helptext', 'Options', 'ValidatorType', 'ValidatorValue', 'ErrorMessage']
header_mandatory = ['Name', 'Type']
vartypes = ['numeric', 'integer', 'varchar', 'select', 'multiple', 'boolean']
vartypes1 = ['select', 'multiple', 'boolean']
dpvalidator = dict(DPVALIDATOR)

rows_list = []
mandatory_index = [header.index(h) for h in header_mandatory]
with open(blueprint_file, newline='') as csvfile:
    blueprints = csv.reader(csvfile, delimiter = '\t')
    for ind, row in enumerate(blueprints):
        if ind == 0:
            # check required columns
            if header == row:
                continue
            else:
                sys.exit(f"Columns are expected in the specified order: {header}")
        # check duplicate rows
        if row in rows_list:
            sys.exit(f"Duplicate row found: {row}")
        # check mandatory fields
        if any([row[m] == '' for m in mandatory_index]):
            sys.exit(f'Mandatory columns missing values: {header_mandatory}')
        # check vartype not in vartypes
        if 'Type' in header_mandatory and row[header.index('Type')] not in vartypes:
            sys.exit(f"'Type' column should contain one of the following types: {vartypes}")
        # create datapoint types
        # check if datapoints already exist
        if DatapointType.objects.filter(name = row[header.index('Name')]).exists():
            # ignore already existing datapoints
            print(f"Warning {row[header.index('Name')]}: Datapoint already exist. Skipping...")
            continue
        if row[header.index('Type')] not in vartypes1 and not any([row[h] == '' for h in [header.index('ValidatorType'), header.index('ValidatorValue')]]):
            # check validators
            validatortypes = [validatortype.strip() for validatortype in row[header.index('ValidatorType')].split(',')]
            validatorvalues = [validatorvalue.strip() for validatorvalue in row[header.index('ValidatorValue')].split(',')]
            validatormsg = row[header.index('ErrorMessage')]
            if len(validatortypes) != len(validatorvalues):
                sys.exit(f"Error {row[header.index('Name')]}: Number of validator types and values does not match")
        # datapointtype
        datapointtype = DatapointType(name = row[header.index('Name')], type = row[header.index('Type')])
        if any([row[header.index('Helptext')] == '', row[header.index('Options')] == '']):
            pass
        else:
            datapointtype.helptext = row[header.index('Helptext')]
        if row[header.index('Type')] in vartypes1:
            options = row[header.index('Options')]
            if options == '':
                sys.exit(f"Error {row[header.index('Name')]}: 'Options' column is mandatory for the following types: {vartypes1}")
            options = [option.strip() for option in options.split(',')]
            if row[header.index('Type')] == 'boolean':
                if len(options) != 2:
                    sys.exit(f"Error {row[header.index('Name')]}: Type 'boolean' should have two Options")
            datapointtype.options = ','.join(options)
        datapointtype.save()
        if row[header.index('Type')] not in vartypes1 and not any([row[h] == '' for h in [header.index('ValidatorType'), header.index('ValidatorValue')]]):
            # validator
            dptvalidator_pks = []
            for i in range(0, len(validatortypes)):
                print(i)
                validator, value, errormsg = validatortypes[i], validatorvalues[i], validatormsg
                validator = list(dpvalidator.keys())[list(dpvalidator.values()).index(validator)]
                if not (validator or value):
                    datapointtype.delete()
                    DatapointValidator.objects.filter(pk__in = dptvalidator_pks).delete()
                    sys.exit(f"Error {row[header.index('Name')]}: Please check the validator type and value")
                response = fn_checkvalidatortype(datapointtype, validator, value)
                if not response['ok']:
                    datapointtype.delete()
                    DatapointValidator.objects.filter(pk__in = dptvalidator_pks).delete()
                    sys.exit(f"Error {row[header.index('Name')]}: {response['message']}")
                datapointvalidator = DatapointValidator(validator = validator, value = value, errormessage = validatormsg)
                datapointvalidator.save()
                dptvalidator_pks.append(datapointvalidator.pk)
                datapointtype.validators.add(datapointvalidator)
        rows_list.append(row)

#############
import csv
import os, sys
from ui.functions import *
from ui.models import DatapointType, DatapointValidator, AnalysisMethod
from ui.choices import DPVALIDATOR

blueprint_file = '../blueprints/method_blueprints.txt'
header = ['Method', 'Datapoints']

rows_list = []
with open(blueprint_file, newline='') as csvfile:
    blueprints = csv.reader(csvfile, delimiter = '\t')
    for ind, row in enumerate(blueprints):
        if ind == 0:
            # check required columns
            if header == row:
                continue
            else:
                sys.exit(f"Columns are expected in the specified order: {header}")
        # check duplicate rows
        if row in rows_list:
            sys.exit(f"Duplicate row found: {row}")
        dptlist = [d.strip() for d in list(set(row[header.index('Datapoints')].split(',')))]
        dptlist_missing = [dpt for dpt in dptlist if not DatapointType.objects.filter(name = dpt).exists()]
        if dptlist_missing:
            sys.exit(f"The datapoints {dptlist_missing} does not exist")
        try:
            analysismethod = AnalysisMethod.objects.get(name = row[header.index('Method')])
            print(f"Analysis method {row[header.index('Method')]} already exist")
        except:
            analysismethod = AnalysisMethod(name = row[header.index('Method')])
            analysismethod.save()
        for dpt in dptlist:
            datapointtype = DatapointType.objects.get(name = dpt)
            datapointtype.rcmd_methods.add(analysismethod)
        rows_list.append(row)