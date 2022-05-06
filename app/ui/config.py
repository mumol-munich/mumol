import variables
from app.settings import APP_PREFIX

content = dict(
    title = variables.title,
    # nav_brand = variables.nav_brand,
    nav_brand = variables.title,
    app_prefix = APP_PREFIX,
    default_none = 'default_none' # donot delete this
)

def add_variable_to_context(request):
    return content
