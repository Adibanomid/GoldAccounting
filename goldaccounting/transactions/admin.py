# transactions/admin.py

from django.contrib import admin

from .models import (
    Branch,
    Counterparty,
    Transaction,
    Payment,
    CardPaymentDetail,
    ChequePaymentDetail,
    MeltedGoldDetail,
    ManufacturedGoldDetail,
    MiscGoldDetail,
    AuditLog,
)


# =====================================================
# Inline Models
# =====================================================

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class MeltedGoldInline(admin.StackedInline):
    model = MeltedGoldDetail
    extra = 0


class ManufacturedGoldInline(admin.StackedInline):
    model = ManufacturedGoldDetail
    extra = 0


class MiscGoldInline(admin.StackedInline):
    model = MiscGoldDetail
    extra = 0


# =====================================================
# Branch
# =====================================================

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
    )
    search_fields = (
        "name",
        "code",
    )


# =====================================================
# Counterparty
# =====================================================

@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "type",
        "mobile",
    )

    list_filter = (
        "type",
    )

    search_fields = (
        "name",
        "mobile",
        "national_code",
    )


# =====================================================
# Transaction
# =====================================================

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "transaction_type",
        "counterparty",
        "branch",
        "gold_category",
        "gold_status",
        "transaction_date",
    )

    list_filter = (
        "transaction_type",
        "gold_category",
        "gold_status",
        "branch",
    )

    search_fields = (
        "id",
        "counterparty__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [
        PaymentInline,
        MeltedGoldInline,
        ManufacturedGoldInline,
        MiscGoldInline,
    ]


# =====================================================
# Payment
# =====================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "transaction",
        "method",
        "amount",
        "status",
    )

    list_filter = (
        "method",
        "status",
    )


# =====================================================
# Card Detail
# =====================================================

@admin.register(CardPaymentDetail)
class CardPaymentDetailAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "payment",
        "reference_number",
        "card_number",
    )


# =====================================================
# Cheque Detail
# =====================================================

@admin.register(ChequePaymentDetail)
class ChequePaymentDetailAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "payment",
        "cheque_number",
        "bank_name",
        "due_date",
    )


# =====================================================
# Audit Log
# =====================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "action",
        "model_name",
        "object_id",
        "created_at",
    )

    readonly_fields = (
        "user",
        "action",
        "model_name",
        "object_id",
        "data",
        "created_at",
    )

    ordering = (
        "-created_at",
    )