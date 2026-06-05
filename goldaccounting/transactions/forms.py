# transactions/forms.py

from django import forms
from django.forms import formset_factory

from .models import (
    TransactionType,
    CounterpartyType,
    GoldCategory,
    NormalGoldType,
    GoldStatus,
    PaymentMethod,
    PaymentStatus,
)


# =====================================================
# Main Transaction Form
# =====================================================

class TransactionCreateForm(forms.Form):

    # -----------------------------------------
    # Transaction
    # -----------------------------------------

    transaction_type = forms.ChoiceField(
        label="نوع معامله",
        choices=TransactionType.choices,
        widget=forms.RadioSelect
    )

    transaction_date = forms.DateTimeField(
        label="تاریخ معامله",
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local"
            }
        )
    )

    # -----------------------------------------
    # Counterparty
    # -----------------------------------------

    counterparty_type = forms.ChoiceField(
        label="نوع طرف معامله",
        choices=CounterpartyType.choices
    )

    counterparty_name = forms.CharField(
        label="نام طرف معامله",
        max_length=255
    )

    counterparty_mobile = forms.CharField(
        label="موبایل",
        required=False
    )

    counterparty_national_code = forms.CharField(
        label="کد ملی",
        required=False
    )

    counterparty_address = forms.CharField(
        label="آدرس",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2})
    )

    # -----------------------------------------
    # Gold
    # -----------------------------------------

    gold_category = forms.ChoiceField(
        label="نوع طلا",
        choices=GoldCategory.choices,
        widget=forms.RadioSelect
    )

    normal_gold_type = forms.ChoiceField(
        label="نوع طلای عادی",
        choices=NormalGoldType.choices,
        required=False
    )

    gold_status = forms.ChoiceField(
        label="وضعیت تحویل طلا",
        choices=GoldStatus.choices,
        initial=GoldStatus.PENDING
    )

    description = forms.CharField(
        label="توضیحات",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3})
    )

    def clean(self):

        cleaned_data = super().clean()

        gold_category = cleaned_data.get("gold_category")
        normal_gold_type = cleaned_data.get("normal_gold_type")

        if (
            gold_category == GoldCategory.NORMAL
            and not normal_gold_type
        ):
            raise forms.ValidationError(
                "نوع طلای عادی را مشخص کنید."
            )

        return cleaned_data


# =====================================================
# Melted Gold Form
# =====================================================

class MeltedGoldForm(forms.Form):

    weight = forms.DecimalField(
        label="وزن",
        decimal_places=3,
        max_digits=12
    )

    assay = forms.DecimalField(
        label="عیار",
        decimal_places=3,
        max_digits=8
    )

    melting_code = forms.CharField(
        label="کد آبشده",
        required=False
    )

    package_number = forms.CharField(
        label="شماره پاکت",
        required=False
    )

    laboratory_number = forms.CharField(
        label="شماره آزمایشگاه",
        required=False
    )


# =====================================================
# Manufactured Gold Form
# =====================================================

class ManufacturedGoldForm(forms.Form):

    weight = forms.DecimalField(
        label="وزن",
        decimal_places=3,
        max_digits=12
    )

    karat = forms.DecimalField(
        label="عیار",
        decimal_places=2,
        max_digits=5
    )

    quantity = forms.IntegerField(
        label="تعداد",
        min_value=1
    )

    wage = forms.DecimalField(
        label="اجرت",
        decimal_places=0,
        max_digits=18
    )

    profit_percent = forms.DecimalField(
        label="درصد سود",
        decimal_places=2,
        max_digits=5
    )

    tax_amount = forms.DecimalField(
        label="مالیات",
        decimal_places=0,
        max_digits=18
    )


# =====================================================
# Misc Gold Form
# =====================================================

class MiscGoldForm(forms.Form):

    weight = forms.DecimalField(
        label="وزن",
        decimal_places=3,
        max_digits=12
    )

    karat = forms.DecimalField(
        label="عیار",
        decimal_places=2,
        max_digits=5
    )

    quantity = forms.IntegerField(
        label="تعداد",
        min_value=1
    )


# =====================================================
# Payment Form
# =====================================================

class PaymentForm(forms.Form):

    method = forms.ChoiceField(
        label="روش پرداخت",
        choices=PaymentMethod.choices
    )

    amount = forms.DecimalField(
        label="مبلغ",
        decimal_places=0,
        max_digits=18
    )

    status = forms.ChoiceField(
        label="وضعیت پرداخت",
        choices=PaymentStatus.choices,
        initial=PaymentStatus.PENDING
    )

    # -----------------------------------------
    # Card fields
    # -----------------------------------------

    reference_number = forms.CharField(
        label="شماره پیگیری",
        required=False
    )

    card_number = forms.CharField(
        label="شماره کارت",
        required=False
    )

    terminal_number = forms.CharField(
        label="شماره دستگاه",
        required=False
    )

    # -----------------------------------------
    # Cheque fields
    # -----------------------------------------

    cheque_number = forms.CharField(
        label="شماره چک",
        required=False
    )

    bank_name = forms.CharField(
        label="نام بانک",
        required=False
    )

    due_date = forms.DateField(
        label="سررسید",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date"}
        )
    )

    account_owner = forms.CharField(
        label="صاحب حساب",
        required=False
    )

    cheque_image = forms.ImageField(
        label="تصویر چک",
        required=False
    )

    def clean(self):

        cleaned_data = super().clean()

        method = cleaned_data.get("method")

        if method == PaymentMethod.CARD:

            if not cleaned_data.get("reference_number"):
                raise forms.ValidationError(
                    "شماره پیگیری کارت الزامی است."
                )

        if method == PaymentMethod.CHEQUE:

            required_fields = [
                "cheque_number",
                "bank_name",
                "due_date",
                "account_owner",
            ]

            for field in required_fields:
                if not cleaned_data.get(field):
                    raise forms.ValidationError(
                        "اطلاعات چک کامل نیست."
                    )

        return cleaned_data


# =====================================================
# Payment Formset
# =====================================================

PaymentFormSet = formset_factory(
    PaymentForm,
    extra=1,
    can_delete=True
)