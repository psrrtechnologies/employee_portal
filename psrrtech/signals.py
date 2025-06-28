# psrrtech/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .models import Employee, IDCard
import datetime


@receiver(post_save, sender=Employee)
def sync_or_create_idcard(sender, instance, created, **kwargs):
    issue_date = instance.date_of_joining or datetime.date.today()
    expiry_date = issue_date + datetime.timedelta(days=365)
    
    branch = instance.branch
    branch_code = branch.code.upper() if branch and branch.code else "XXX"
    year = issue_date.year

    idcard_data = {
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "location": branch,
        "designation": instance.designation,
        "department": instance.department,
        "date_of_birth": instance.date_of_birth,
        "date_of_joining": instance.date_of_joining,
    }

    try:
        # Update existing IDCard
        idcard = IDCard.objects.get(employee=instance)
        for field, value in idcard_data.items():
            setattr(idcard, field, value)
        idcard.save()

    except IDCard.DoesNotExist:
        # Create a unique ID number
        count = IDCard.objects.filter(
            employee__branch=branch,
            issue_date__year=year
        ).count() + 1
        serial = f"{count:03d}"
        id_number = f"PSRR-{branch_code}-{year}-{serial}"

        # Create new IDCard
        IDCard.objects.create(
            employee=instance,
            id_number=id_number,
            **idcard_data
        )