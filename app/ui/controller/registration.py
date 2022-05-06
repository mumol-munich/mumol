from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login

from ..decorators import nologin_required
from ..forms import RegisterForm

@nologin_required
def registration(request):
    form = RegisterForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Login successful!")
            return HttpResponseRedirect(reverse('index'))
        else:
            messages.error(request, form.errors)
    return render(request, 'registration/registration.html', dict(form=form))
