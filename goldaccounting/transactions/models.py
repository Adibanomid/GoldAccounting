# transactions/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone


# =====================================================
# Branch
# =====================================================

class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


# =====================================================
# Choices
# =====================================================

class TransactionType(models.TextChoices):
    BUY = "buy", "خرید"
    SELL = "sell", "فروش"


class CounterpartyType(models.TextChoices):
    CUSTOMER = "customer", "مشتری"
    COLLEAGUE = "colleague", "همکار"
    WHOLESALER = "wholesaler", "بنکدار"
    MELTED_GOLD_SELLER = "melted_gold_seller", "آبشده فروش"
    GOLD_BANK = "gold_bank", "بانک طلا"


class GoldCategory(models.TextChoices):
    MELTED = "melted", "طلای آبشده"
    NORMAL = "normal", "طلای عادی"


class NormalGoldType(models.TextChoices):
    MANUFACTURED = "manufactured", "طلای ساخته"
    MISC = "misc", "طلای متفرقه"


class GoldStatus(models.TextChoices):
    PENDING = "pending", "در انتظار"
    DELIVERED = "delivered", "تحویل شده"


class PaymentMethod(models.TextChoices):
    CASH = "cash", "نقد"
    CARD = "card", "کارت"
    CHEQUE = "cheque", "چک"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "در انتظار"
    DONE = "done", "انجام شده"
    CANCELLED = "cancelled", "لغو شده"


# =====================================================
# Counterparty
# =====================================================

class Counterparty(models.Model):
    name = models.CharField(max_length=255)

    type = models.CharField(
        max_length=50,
        choices=CounterpartyType.choices
    )

    mobile = models.CharField(
        max_length=20,
        blank=True
    )

    national_code = models.CharField(
        max_length=20,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


# =====================================================
# Main Transaction
# =====================================================

class Transaction(models.Model):

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices
    )

    counterparty = models.ForeignKey(
        Counterparty,
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_transactions"
    )

    transaction_date = models.DateTimeField(
        default=timezone.now
    )

    gold_category = models.CharField(
        max_length=20,
        choices=GoldCategory.choices
    )

    normal_gold_type = models.CharField(
        max_length=20,
        choices=NormalGoldType.choices,
        blank=True
    )

    gold_status = models.CharField(
        max_length=20,
        choices=GoldStatus.choices,
        default=GoldStatus.PENDING
    )

    gold_delivered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-transaction_date"]

    def __str__(self):
        return f"#{self.pk} - {self.get_transaction_type_display()}"


# =====================================================
# Melted Gold Details
# =====================================================

class MeltedGoldDetail(models.Model):

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name="melted_gold"
    )

    weight = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    assay = models.DecimalField(
        max_digits=8,
        decimal_places=3
    )

    melting_code = models.CharField(
        max_length=100,
        blank=True
    )

    package_number = models.CharField(
        max_length=100,
        blank=True
    )

    laboratory_number = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return f"Melted Gold - Tx {self.transaction_id}"


# =====================================================
# Manufactured Gold
# =====================================================

class ManufacturedGoldDetail(models.Model):

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name="manufactured_gold"
    )

    weight = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    karat = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    wage = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0
    )

    profit_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0
    )

    def __str__(self):
        return f"Manufactured Gold - Tx {self.transaction_id}"


# =====================================================
# Misc Gold
# =====================================================

class MiscGoldDetail(models.Model):

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name="misc_gold"
    )

    weight = models.DecimalField(
        max_digits=12,
        decimal_places=3
    )

    karat = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    def __str__(self):
        return f"Misc Gold - Tx {self.transaction_id}"


# =====================================================
# Payments
# =====================================================

class Payment(models.Model):

    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=0
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.method} - {self.amount}"


# =====================================================
# Card Payment Details
# =====================================================

class CardPaymentDetail(models.Model):

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="card_detail"
    )

    reference_number = models.CharField(
        max_length=100
    )

    card_number = models.CharField(
        max_length=30,
        blank=True
    )

    terminal_number = models.CharField(
        max_length=50,
        blank=True
    )


# =====================================================
# Cheque Details
# =====================================================

class ChequePaymentDetail(models.Model):

    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="cheque_detail"
    )

    cheque_number = models.CharField(
        max_length=100
    )

    bank_name = models.CharField(
        max_length=255
    )

    due_date = models.DateField()

    account_owner = models.CharField(
        max_length=255
    )

    image = models.ImageField(
        upload_to="cheques/",
        blank=True,
        null=True
    )


# =====================================================
# Audit Log
# =====================================================

class AuditLog(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(
        max_length=255
    )

    model_name = models.CharField(
        max_length=255
    )

    object_id = models.PositiveBigIntegerField()

    data = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.model_name}"