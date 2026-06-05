# transactions/validators.py

from decimal import Decimal

from django.core.exceptions import ValidationError

from .models import (
    GoldCategory,
    NormalGoldType,
    PaymentMethod,
)


# =====================================================
# Transaction Validation
# =====================================================

def validate_transaction_data(data):

    gold_category = data.get("gold_category")
    normal_gold_type = data.get("normal_gold_type")

    if (
        gold_category == GoldCategory.NORMAL
        and not normal_gold_type
    ):
        raise ValidationError(
            "برای طلای عادی باید نوع آن مشخص شود."
        )


# =====================================================
# Melted Gold Validation
# =====================================================

def validate_melted_gold(data):

    weight = data.get("weight")
    assay = data.get("assay")

    if weight is None or weight <= 0:
        raise ValidationError(
            "وزن آبشده باید بیشتر از صفر باشد."
        )

    if assay is None or assay <= 0:
        raise ValidationError(
            "عیار آبشده نامعتبر است."
        )


# =====================================================
# Manufactured Gold Validation
# =====================================================

def validate_manufactured_gold(data):

    weight = data.get("weight")
    quantity = data.get("quantity")

    if weight <= 0:
        raise ValidationError(
            "وزن باید بیشتر از صفر باشد."
        )

    if quantity <= 0:
        raise ValidationError(
            "تعداد باید بیشتر از صفر باشد."
        )


# =====================================================
# Misc Gold Validation
# =====================================================

def validate_misc_gold(data):

    weight = data.get("weight")
    quantity = data.get("quantity")

    if weight <= 0:
        raise ValidationError(
            "وزن باید بیشتر از صفر باشد."
        )

    if quantity <= 0:
        raise ValidationError(
            "تعداد باید بیشتر از صفر باشد."
        )


# =====================================================
# Payment Validation
# =====================================================

def validate_payment(payment):

    method = payment.get("method")
    amount = payment.get("amount")

    if amount is None:
        raise ValidationError(
            "مبلغ پرداخت الزامی است."
        )

    if Decimal(amount) <= 0:
        raise ValidationError(
            "مبلغ باید بیشتر از صفر باشد."
        )

    if method == PaymentMethod.CARD:
        validate_card_payment(payment)

    elif method == PaymentMethod.CHEQUE:
        validate_cheque_payment(payment)


# =====================================================
# Card Validation
# =====================================================

def validate_card_payment(payment):

    if not payment.get("reference_number"):
        raise ValidationError(
            "شماره پیگیری کارت الزامی است."
        )


# =====================================================
# Cheque Validation
# =====================================================

def validate_cheque_payment(payment):

    required_fields = [
        "cheque_number",
        "bank_name",
        "due_date",
        "account_owner",
    ]

    for field in required_fields:

        if not payment.get(field):

            raise ValidationError(
                f"{field} الزامی است."
            )


# =====================================================
# Full Transaction Validation
# =====================================================

def validate_complete_transaction(
    transaction_data,
    melted_data=None,
    manufactured_data=None,
    misc_data=None,
    payments=None,
):

    validate_transaction_data(
        transaction_data
    )

    if (
        transaction_data["gold_category"]
        == GoldCategory.MELTED
    ):
        validate_melted_gold(
            melted_data or {}
        )

    elif (
        transaction_data["gold_category"]
        == GoldCategory.NORMAL
    ):

        if (
            transaction_data["normal_gold_type"]
            == NormalGoldType.MANUFACTURED
        ):
            validate_manufactured_gold(
                manufactured_data or {}
            )

        elif (
            transaction_data["normal_gold_type"]
            == NormalGoldType.MISC
        ):
            validate_misc_gold(
                misc_data or {}
            )

    for payment in payments or []:
        validate_payment(payment)