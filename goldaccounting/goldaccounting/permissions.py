
from django.contrib.auth.models import Group, Permission

ROLES = [
    "Seller",
    "BankOfficer",
    "Accountant",
    "AccountingSupervisor",
    "StoreManager",
]

def create_roles():
    for role in ROLES:
        Group.objects.get_or_create(name=role)
