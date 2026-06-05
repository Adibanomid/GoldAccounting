# transactions/permissions.py

from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied


# =====================================================
# Group Names
# =====================================================

SELLER = "Seller"
BANK_OFFICER = "BankOfficer"
ACCOUNTANT = "Accountant"
ACCOUNTING_SUPERVISOR = "AccountingSupervisor"
STORE_MANAGER = "StoreManager"


# =====================================================
# Helpers
# =====================================================

def user_in_group(user, group_name):
    return user.groups.filter(
        name=group_name
    ).exists()


def require_group(user, groups):

    if not user.is_authenticated:
        raise PermissionDenied()

    if user.is_superuser:
        return True

    if isinstance(groups, str):
        groups = [groups]

    if any(
        user_in_group(user, group)
        for group in groups
    ):
        return True

    raise PermissionDenied()


# =====================================================
# Transaction Permissions
# =====================================================

def can_create_transaction(user):

    return any([
        user_in_group(user, SELLER),
        user_in_group(user, ACCOUNTANT),
        user_in_group(user, ACCOUNTING_SUPERVISOR),
        user_in_group(user, STORE_MANAGER),
    ])


def can_edit_transaction(user):

    return any([
        user_in_group(user, ACCOUNTANT),
        user_in_group(user, ACCOUNTING_SUPERVISOR),
        user_in_group(user, STORE_MANAGER),
    ])


def can_delete_transaction(user):

    return any([
        user_in_group(user, ACCOUNTING_SUPERVISOR),
        user_in_group(user, STORE_MANAGER),
    ])


# =====================================================
# Payment Permissions
# =====================================================

def can_change_payment_status(user):

    return any([
        user_in_group(user, BANK_OFFICER),
        user_in_group(user, ACCOUNTANT),
        user_in_group(user, ACCOUNTING_SUPERVISOR),
        user_in_group(user, STORE_MANAGER),
    ])


# =====================================================
# Gold Delivery Permissions
# =====================================================

def can_change_gold_status(user):

    return any([
        user_in_group(user, SELLER),
        user_in_group(user, ACCOUNTANT),
        user_in_group(user, ACCOUNTING_SUPERVISOR),
        user_in_group(user, STORE_MANAGER),
    ])


# =====================================================
# Reports Permissions
# =====================================================

def can_view_reports(user):

    return any([
        user_in_group(user, ACCOUNTANT),
        user_in_group(user, ACCOUNTING_SUPERVISOR),
        user_in_group(user, STORE_MANAGER),
    ])


# =====================================================
# User Management
# =====================================================

def can_manage_users(user):

    return any([
        user_in_group(user, STORE_MANAGER),
    ])


# =====================================================
# Example Mixins
# =====================================================

class SellerRequiredMixin:

    def dispatch(self, request, *args, **kwargs):

        require_group(
            request.user,
            [
                SELLER,
                ACCOUNTANT,
                ACCOUNTING_SUPERVISOR,
                STORE_MANAGER,
            ]
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


class AccountantRequiredMixin:

    def dispatch(self, request, *args, **kwargs):

        require_group(
            request.user,
            [
                ACCOUNTANT,
                ACCOUNTING_SUPERVISOR,
                STORE_MANAGER,
            ]
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )


class BankOfficerRequiredMixin:

    def dispatch(self, request, *args, **kwargs):

        require_group(
            request.user,
            [
                BANK_OFFICER,
                ACCOUNTING_SUPERVISOR,
                STORE_MANAGER,
            ]
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )