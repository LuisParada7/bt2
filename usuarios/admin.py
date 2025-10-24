from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')

class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = UserResource

admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)
