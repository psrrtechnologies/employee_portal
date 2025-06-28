from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from psrrtech.models import Profile, Employee
from psrrtech.forms import UserCreationWithEmployeeForm
from psrrtech.utils import generate_unique_username  # you should have this in utils.py
from .models import (
    Branch,
    Employee,
    Workstation,
    IDCard,
    BankDetails,
    Attendance,
    Payroll,
    Profile  # optional if not already added inline
)

admin.site.register(Branch)
admin.site.register(Employee)
admin.site.register(Workstation)
admin.site.register(IDCard)
admin.site.register(BankDetails)
admin.site.register(Attendance)
admin.site.register(Payroll)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationWithEmployeeForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('employee', 'first_name', 'last_name', 'email', 'username', 'password1', 'password2'),
        }),
    )
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_select_related = ('profile',)

    def get_role(self, instance):
        return instance.profile.role if hasattr(instance, 'profile') else "-"
    get_role.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        employee = form.cleaned_data.get('employee')

        # Auto-fill from employee if linked
        if employee:
            obj.first_name = employee.first_name
            obj.last_name = employee.last_name
            obj.email = employee.email

            if not obj.username:
                obj.username = generate_unique_username(employee.first_name, employee.last_name)

        super().save_model(request, obj, form, change)

        # Link employee to user
        if employee:
            employee.user = obj
            employee.save()

# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
