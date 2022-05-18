import os
import sys
import subprocess
import venv
import shutil
from copy import deepcopy

from optparse import OptionParser

parser = OptionParser()
parser.add_option("", "--venv-path", dest="venv_path",
                  default = 'venv',
                  help="Virtual environment path (default: venv)")
(options, args) = parser.parse_args()

# check python version
print('Checking python version...')
if not sys.version_info >= (3, ):
    sys.exit('Please execute it with python 3')

# check datamask
print('Checking source directory...')
try:
    datamask = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
except:
    datamask = "."

if not os.path.isfile(f'{datamask}/setup/install.py'):
    sys.exit('Please execute it from datamsk directory')
os.chdir(datamask)

# check variables.py or variables.py.sample
print('Checking variables.py file...')
if os.path.isfile(f'{datamask}/app/variables.py'):
    print('File exist.')
elif os.path.isfile(f'{datamask}/app/variables.py.sample'):
    print('Copying variables.py.sample as variables.py...')
    shutil.copyfile(f'{datamask}/app/variables.py.sample', f'{datamask}/app/variables.py')
else:
    sys.exit('variables.py or variables.py.sample does not exist.')

# check pip requirements
print('Check pip requirements file...')
if not os.path.isfile(f'{datamask}/setup/requirements.txt'):
    sys.exit('pip requirements file not found. Please download the recent version')

# check package.json
print('Check package.json file...')
if not os.path.isfile(f'{datamask}/app/ui/static/package.json'):
    sys.exit('package.json not found. Please download the recent version')

# set abs path
if options.venv_path.startswith('/'):
    venv_path = options.venv_path
else:
    venv_path = os.path.abspath(options.venv_path)

# create venv
print('Creating virtual environment...')
print(os.path.abspath(venv_path))
venvbuilder = venv.EnvBuilder(with_pip = True)
venvbuilder.create(venv_path)

# check platform
print('Checking system platform...')
if sys.platform == 'linux':
    binpath = f'{venv_path}/bin'
    shell_switch = False
elif 'win' in sys.platform:
    binpath = f'{venv_path}/Scripts'
    shell_switch = True
else:
    sys.exit('Unknown system platform')
# some venv based issue while installing in windows. shell_switch clears this issue somehow

# install pip requirements
print('Install requirements...')
process = subprocess.Popen([f'{binpath}/pip3', 'install', '-r', f'{datamask}/setup/requirements.txt', '--trusted-host', 'pypi.org', '--trusted-host', 'files.pythonhosted.org'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
while process.poll() is None:
    print(process.stdout.readline())

process.stdout.read()
process.stdout.close()

# make migrations
print('Detecting changes in the database...')
process = subprocess.Popen([f'{binpath}/python', f'{datamask}/app/manage.py', 'makemigrations'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
while process.poll() is None:
    print(process.stdout.readline())
    print(process.stderr.readline())

process.stdout.read()
process.stderr.read()
process.stdout.close()
process.stderr.close()


# migrate
print('Migrate changes if necessary...')
process = subprocess.Popen([f'{binpath}/python', f'{datamask}/app/manage.py', 'migrate'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
while process.poll() is None:
    print(process.stdout.readline())
    print(process.stderr.readline())

process.stdout.read()
process.stderr.read()
process.stdout.close()
process.stderr.close()


print('Initial setup complete.')
print(f'''
Please execute the following from source directory ({datamask}/app),

# linux
source {venv_path}/bin/activate && python {datamask}/app/manage.py runserver

# windows
{venv_path}\\Scripts\\activate && python {datamask}/app/manage.py runserver


END
please close the window or hit enter key
''')

input()