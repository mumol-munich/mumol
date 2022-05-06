# create env
conda create --name nngm python=3
conda activate nngm

# install requirements
pip install -r init/requirements.txt

# create project app
django-admin startproject app
cd app
python manage.py startapp ui
python manage.py startapp rest


# After defining models
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# create superuser
python manage.py createsuperuser --email admin@example.com --username admin

# reset migrations
python manage.py migrate --fake ui zero
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
python manage.py makemigrations
python manage.py migrate --fake-initial


# # typescript
conda install -c conda-forge nodejs #12.19.0
npm install -g typescript

# npm install -g @angular/cli #11.0.0
# cd ui
# ng new front-end
# # add outputPath of static files to angular.json "../static/front-end"

# ng build

# ng generate component home
# ng generate component about

# ng add @angular/material@7.3.2


# ng generate service data
cd /home/nazeer/Documents/nNGM/datamask/app/ui/static
tsc --init
npm install @types/jquery
npm install mdbootstrap
npm install select2
npm install --save @types/select2
npm install local-storage --save
# npm install typescript-require
npm install handlebars

# npm install -g bower
# npm install bootstrap-treeview
# npm install --save bootstrap-toggle

# conda install -c anaconda graphviz

# python ../manage.py graph_models ui > ui.dot
# dot -Tpng ui.dot -o ui.png


# nodeenv -p

python ../app/manage.py graph_models -a -o ui1.png
python ../app/manage.py graph_models -a --hide-edge-labels -o ui2.png
python ../app/manage.py graph_models -a --arrow-shape normal -o ui3.png
python ../app/manage.py graph_models -a --arrow-shape normal --hide-edge-labels -o ui4.png

python ../app/manage.py graph_models -a -g -o ui5.png