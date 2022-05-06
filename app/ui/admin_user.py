from django.contrib.auth.models import User

admin_email = "admin@example.com"
admin_user = "admin"

try:
    user = User.objects.get(email = admin_email)
except:
    user = User.objects.create_user(username = admin_user, email = admin_email, password = 'admin')
    print("admin user created successfully")

# set profile isadmin
if not user.profile.is_admin:
    user.profile.is_admin = True
    user.save()