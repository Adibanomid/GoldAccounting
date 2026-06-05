from django.db import models
from django.contrib.auth.models import AbstractUser,User


class Branch(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# class User(AbstractUser):
#     branch = models.ForeignKey(
#         Branch,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="users"
#     )


class CounterpartyType(models.TextChoices):
    CUSTOMER = "customer", "مشتری"
    COLLEAGUE = "colleague", "همکار"
    WHOLESALER = "wholesaler", "بنکدار"
    MELTED_GOLD_SELLER = "melted_gold_seller", "آبشده فروش"
    GOLD_BANK = "gold_bank", "بانک طلا"


class Counterparty(models.Model):
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=30, blank=True)
    national_code = models.CharField(max_length=20, blank=True)
    type = models.CharField(max_length=50, choices=CounterpartyType.choices)

    def __str__(self):
        return self.name


class TransactionType(models.TextChoices):
    BUY = "buy", "خرید"
    SELL = "sell", "فروش"


class GoldCategory(models.TextChoices):
    MELTED = "melted", "طلای آبشده"
    NORMAL = "normal", "طلای عادی"


class NormalGoldType(models.TextChoices):
    MANUFACTURED = "manufactured", "طلای ساخته"
    MISC = "misc", "متفرقه"


class GoldDeliveryStatus(models.TextChoices):
    PENDING = "pending", "در انتظار"
    DELIVERED = "delivered", "تحویل شده"


class Transaction(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    counterparty = models.ForeignKey(Counterparty, on_delete=models.PROTECT)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    transaction_date = models.DateTimeField()

    gold_status = models.CharField(
        max_length=20,
        choices=GoldDeliveryStatus.choices,
        default=GoldDeliveryStatus.PENDING
    )
    gold_delivered_at = models.DateTimeField(null=True, blank=True)

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} #{self.pk}"


class TransactionGold(models.Model):
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name="gold"
    )
    category = models.CharField(max_length=20, choices=GoldCategory.choices)


class MeltedGoldDetail(models.Model):
    gold = models.OneToOneField(
        TransactionGold,
        on_delete=models.CASCADE,
        related_name="melted_detail"
    )
    weight = models.DecimalField(max_digits=12, decimal_places=3)
    assay = models.DecimalField(max_digits=8, decimal_places=3)


class NormalGoldDetail(models.Model):
    gold = models.OneToOneField(
        TransactionGold,
        on_delete=models.CASCADE,
        related_name="normal_detail"
    )
    normal_type = models.CharField(max_length=20, choices=NormalGoldType.choices)
    weight = models.DecimalField(max_digits=12, decimal_places=3)
    karat = models.DecimalField(max_digits=5, decimal_places=2)


class PaymentMethod(models.TextChoices):
    CASH = "cash", "نقد"
    CARD = "card", "کارت"
    CHEQUE = "cheque", "چک"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "در انتظار"
    DONE = "done", "انجام شده"


class Payment(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        related_name="payments",
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    paid_at = models.DateTimeField(null=True, blank=True)


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    object_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
