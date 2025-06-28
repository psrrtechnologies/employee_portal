from django.db import models
from django.contrib.auth.models import User
import datetime
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

# Optional: Country utility (you can define get_country_from_phone in utils.py)
# from .utils import get_country_from_phone

# -------------------------
# Branch Model
# -------------------------
class Branch(models.Model):
    NAME_CHOICES = [
        ('AREHUDEM', 'Aregudem'),
        ('HYDERABAD', 'Hyderabad'),
        ('UNITED STATES', 'United States'),
    ]
    name = models.CharField(max_length=20, choices=NAME_CHOICES)
    code = models.CharField(max_length=10, unique=True)
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# -------------------------
# Employee Model
# -------------------------
class Employee(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    ]

    DEPARTMENT_CHOICES = [
        ('ADMIN', 'Administration'),
        ('HR', 'Human Resources'),
        ('EMPLOYEE', 'Employee'),
    ]

    EMPLOYMENT_CHOICES = [
        ('FULL-TIME', 'Full-Time'),
        ('PADRT-TIME', 'Part-Time'),
    ]

    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    employee_id = models.CharField(max_length=30, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='EMPLOYEE')
    designation = models.CharField(max_length=100)
    date_of_joining = models.DateField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, default='FULL_TIME')
    address_line_1 = models.TextField()
    address_line_2 = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    date_of_termination = models.DateField(null=True, blank=True)
    tax_id = models.CharField(max_length=10,unique=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.employee_id and self.branch:
            branch_code = self.branch.code.upper()
            existing_count = Employee.objects.filter(branch=self.branch).count() + 1
            serial = f"{existing_count:03d}"
            self.employee_id = f"PSRR-{branch_code}-{serial}"
        # self.country = get_country_from_phone(self.phone_number)  # Optional
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"


# -------------------------
# Workstation Model
# -------------------------
class Workstation(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    desk_number = models.CharField(max_length=20, unique=True)
    floor = models.CharField(max_length=10)
    building = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    device_type = models.CharField(max_length=30)
    device_make = models.CharField(max_length=30)
    device_model = models.CharField(max_length=50)
    device_serial_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Desk {self.desk_number} - {self.employee.full_name}"


# -------------------------
# ID Card Model
# -------------------------
class IDCard(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=30, unique=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='id_photos/', blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, to_field='code')
    designation = models.CharField(max_length=100, editable=False)
    department = models.CharField(max_length=100, editable=False)
    date_of_birth = models.DateField(editable=False)
    date_of_joining = models.DateField(editable=False)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={
        'profile__role__in': ['hr', 'admin']
    })
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES,null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        branch_code = self.employee.branch.code.upper() if self.employee and self.employee.branch else "XXX"
        if not self.id_number:
            branch_code = self.employee.branch.code.upper() if self.employee.branch else "XXX"
            year = datetime.datetime.now().year
            count = IDCard.objects.filter(
                employee__branch=self.employee.branch,
                issue_date__year=year
            ).count() + 1
            serial = f"{count:03d}"
            self.id_number = f"PSRR-{branch_code}-{year}-{serial}"

        # Sync employee details
        self.designation = self.employee.designation
        self.department = self.employee.department
        self.date_of_birth = self.employee.date_of_birth
        self.date_of_joining = self.employee.date_of_joining

        super().save(*args, **kwargs)

        if not self.qr_code:
            qr_data = f"Employee: {self.employee.full_name}\nID: {self.id_number}\nBranch: {branch_code}"
            qr_img = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            self.qr_code.save(f'{self.id_number}_qr.png', ContentFile(buffer.getvalue()), save=False)
            super().save(update_fields=['qr_code'])

    def __str__(self):
        return f"ID Card - {self.employee.full_name}"


# -------------------------
# Bank Details Model
# -------------------------
class BankDetails(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30, unique=True)
    ifsc_code = models.CharField(max_length=20)
    branch = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20)  # e.g., Savings, Current
    swift_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Bank - {self.employee.full_name}"


# -------------------------
# Attendance Model
# -------------------------
class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    status = models.CharField(max_length=10)  # Present, Absent, Leave

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.date} - {self.employee.full_name}"


# -------------------------
# Payroll Model
# -------------------------
class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    bank_account = models.ForeignKey(BankDetails, on_delete=models.SET_NULL, null=True, blank=True)
    month = models.CharField(max_length=10)
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()

    class Meta:
        unique_together = ('employee', 'month', 'year')

    def __str__(self):
        return f"{self.month} {self.year} - {self.employee.full_name}"

    def account_info(self):
        return self.bank_account.account_number if self.bank_account else "No Account Linked"


# -------------------------
# Profile Model for Role-Based Access
# -------------------------
class Profile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('employee', 'Employee'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
