# transactions/views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction as db_transaction
from django.shortcuts import render, redirect
from django.views import View

from .forms import (
    TransactionCreateForm,
    MeltedGoldForm,
    ManufacturedGoldForm,
    MiscGoldForm,
    PaymentFormSet,
)

from .models import (
    Counterparty,
    Transaction,
    GoldCategory,
    NormalGoldType,
    Payment,
    PaymentMethod,
    CardPaymentDetail,
    ChequePaymentDetail,
    MeltedGoldDetail,
    ManufacturedGoldDetail,
    MiscGoldDetail,
    AuditLog,
)


class TransactionCreateView(LoginRequiredMixin, View):

    template_name = "transactions/create.html"

    def get(self, request):

        context = {
            "transaction_form": TransactionCreateForm(),
            "melted_form": MeltedGoldForm(),
            "manufactured_form": ManufacturedGoldForm(),
            "misc_form": MiscGoldForm(),
            "payment_formset": PaymentFormSet(),
        }

        return render(
            request,
            self.template_name,
            context,
        )

    @db_transaction.atomic
    def post(self, request):

        transaction_form = TransactionCreateForm(
            request.POST
        )

        melted_form = MeltedGoldForm(
            request.POST,
            prefix="melted"
        )

        manufactured_form = ManufacturedGoldForm(
            request.POST,
            prefix="manufactured"
        )

        misc_form = MiscGoldForm(
            request.POST,
            prefix="misc"
        )

        payment_formset = PaymentFormSet(
            request.POST,
            request.FILES,
            prefix="payments"
        )

        if not transaction_form.is_valid():

            return render(
                request,
                self.template_name,
                {
                    "transaction_form": transaction_form,
                    "melted_form": melted_form,
                    "manufactured_form": manufactured_form,
                    "misc_form": misc_form,
                    "payment_formset": payment_formset,
                }
            )

        # ------------------------------------
        # Counterparty
        # ------------------------------------

        counterparty, _ = Counterparty.objects.get_or_create(
            name=transaction_form.cleaned_data[
                "counterparty_name"
            ],
            defaults={
                "type": transaction_form.cleaned_data[
                    "counterparty_type"
                ],
                "mobile": transaction_form.cleaned_data[
                    "counterparty_mobile"
                ],
                "national_code": transaction_form.cleaned_data[
                    "counterparty_national_code"
                ],
                "address": transaction_form.cleaned_data[
                    "counterparty_address"
                ],
            }
        )

        # ------------------------------------
        # Transaction
        # ------------------------------------

        trx = Transaction.objects.create(
            branch=request.user.branch,
            transaction_type=transaction_form.cleaned_data[
                "transaction_type"
            ],
            transaction_date=transaction_form.cleaned_data[
                "transaction_date"
            ],
            counterparty=counterparty,
            created_by=request.user,
            gold_category=transaction_form.cleaned_data[
                "gold_category"
            ],
            normal_gold_type=transaction_form.cleaned_data[
                "normal_gold_type"
            ],
            gold_status=transaction_form.cleaned_data[
                "gold_status"
            ],
            description=transaction_form.cleaned_data[
                "description"
            ],
        )

        # ------------------------------------
        # Gold Details
        # ------------------------------------

        if trx.gold_category == GoldCategory.MELTED:

            if melted_form.is_valid():

                MeltedGoldDetail.objects.create(
                    transaction=trx,
                    weight=melted_form.cleaned_data["weight"],
                    assay=melted_form.cleaned_data["assay"],
                    melting_code=melted_form.cleaned_data["melting_code"],
                    package_number=melted_form.cleaned_data["package_number"],
                    laboratory_number=melted_form.cleaned_data["laboratory_number"],
                )

        elif (
            trx.gold_category == GoldCategory.NORMAL
            and trx.normal_gold_type
            == NormalGoldType.MANUFACTURED
        ):

            if manufactured_form.is_valid():

                ManufacturedGoldDetail.objects.create(
                    transaction=trx,
                    weight=manufactured_form.cleaned_data["weight"],
                    karat=manufactured_form.cleaned_data["karat"],
                    quantity=manufactured_form.cleaned_data["quantity"],
                    wage=manufactured_form.cleaned_data["wage"],
                    profit_percent=manufactured_form.cleaned_data["profit_percent"],
                    tax_amount=manufactured_form.cleaned_data["tax_amount"],
                )

        elif (
            trx.gold_category == GoldCategory.NORMAL
            and trx.normal_gold_type
            == NormalGoldType.MISC
        ):

            if misc_form.is_valid():

                MiscGoldDetail.objects.create(
                    transaction=trx,
                    weight=misc_form.cleaned_data["weight"],
                    karat=misc_form.cleaned_data["karat"],
                    quantity=misc_form.cleaned_data["quantity"],
                )

        # ------------------------------------
        # Payments
        # ------------------------------------

        if payment_formset.is_valid():

            for form in payment_formset:

                if not form.cleaned_data:
                    continue

                if form.cleaned_data.get("DELETE"):
                    continue

                payment = Payment.objects.create(
                    transaction=trx,
                    method=form.cleaned_data["method"],
                    amount=form.cleaned_data["amount"],
                    status=form.cleaned_data["status"],
                )

                # CARD

                if (
                    payment.method
                    == PaymentMethod.CARD
                ):

                    CardPaymentDetail.objects.create(
                        payment=payment,
                        reference_number=form.cleaned_data[
                            "reference_number"
                        ],
                        card_number=form.cleaned_data[
                            "card_number"
                        ],
                        terminal_number=form.cleaned_data[
                            "terminal_number"
                        ],
                    )

                # CHEQUE

                elif (
                    payment.method
                    == PaymentMethod.CHEQUE
                ):

                    ChequePaymentDetail.objects.create(
                        payment=payment,
                        cheque_number=form.cleaned_data[
                            "cheque_number"
                        ],
                        bank_name=form.cleaned_data[
                            "bank_name"
                        ],
                        due_date=form.cleaned_data[
                            "due_date"
                        ],
                        account_owner=form.cleaned_data[
                            "account_owner"
                        ],
                        image=form.cleaned_data.get(
                            "cheque_image"
                        ),
                    )

        # ------------------------------------
        # Audit Log
        # ------------------------------------

        AuditLog.objects.create(
            user=request.user,
            action="create",
            model_name="Transaction",
            object_id=trx.id,
            data={
                "transaction_type": trx.transaction_type,
                "counterparty": counterparty.name,
            }
        )

        messages.success(
            request,
            "معامله با موفقیت ثبت شد."
        )

        return redirect(
            "transactions:detail",
            pk=trx.pk
        )


class TransactionDetailView(
    LoginRequiredMixin,
    View
):

    template_name = "transactions/detail.html"

    def get(self, request, pk):

        trx = Transaction.objects.select_related(
            "counterparty"
        ).prefetch_related(
            "payments"
        ).get(pk=pk)

        return render(
            request,
            self.template_name,
            {
                "transaction": trx
            }
        )