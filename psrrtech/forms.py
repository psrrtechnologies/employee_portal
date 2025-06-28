from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from psrrtech.models import Employee

class UserCreationWithEmployeeForm(UserCreationForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(user__isnull=True),
        required=False,
        help_text="Link this user to an existing employee (optional)"
    )

    class Meta:
        model = User
        fields = ("employee", "first_name", "last_name", "email", "username")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mark auto-filled fields as not required when employee is selected
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['email'].required = False
        self.fields['username'].required = False
