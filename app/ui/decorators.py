from django.contrib.auth.decorators import user_passes_test
from app.settings import LOGIN_URL, _APP_PREFIX, APP_PREFIX

index_url = f'{_APP_PREFIX}/'


def nologin_required(function=None):
    ''' Only allowing user without login credentials '''
    actual_decorator = user_passes_test(
        lambda u: not u.id, login_url=index_url)
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_required(function=None):
    ''' Only allowing user without login credentials '''
    actual_decorator = user_passes_test(
        lambda u: u.profile.is_admin, login_url=index_url)
    if function:
        return actual_decorator(function)
    return actual_decorator


# def check_project_user(function = None, project_pk = None):
#     actual_decorator = False
#     if project_pk:
#         actual_decorator = user_passes_test(
#             lambda u: u.profile.is_admin or u.project_user.filter(pk = project_pk).exists(), login_url = index_url)
#         if function:
#             return actual_decorator(function)
#     return actual_decorator
