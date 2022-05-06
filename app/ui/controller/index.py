from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from ..models import Project

import json

def index(request):
    project_redirect = request.GET.get('project_redirect')
    first_project_id = False
    if request.user.id:
        if request.user.project_user.exists():
            first_project_id = request.user.project_user.first().pk
        elif request.user.profile.is_admin:
            if Project.objects.exists():
                first_project_id = Project.objects.first().pk
            else:
                first_project_id = False
                project_redirect = False
        else:
            first_project_id = False
            project_redirect = False
    # return HttpResponse(json.dumps(dict(project_redirect = project_redirect, first_project_id = first_project_id)))
    return render(request, 'ui_new/home/index.html', dict(project_redirect = project_redirect, first_project_id = first_project_id))

def view_404(request, exception = None):
    # messages.error(request, '404 Page not found.')
    return HttpResponseRedirect(reverse('index'))