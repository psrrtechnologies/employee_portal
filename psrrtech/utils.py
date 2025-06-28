from django.contrib.auth.models import User


def get_country_from_phone(phone_number):
    # Dummy logic – replace with actual phone parsing if needed
    if phone_number.startswith('+91'):
        return 'India'
    elif phone_number.startswith('+1'):
        return 'United States'
    else:
        return 'Unknown'
    

def generate_unique_username(first_name, last_name):
    base_username = f"{first_name.lower()}.{last_name.lower()}".replace(" ", "")
    username = base_username
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    return username    