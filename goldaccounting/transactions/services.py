# transactions/services.py

from django.db import transaction as db_transaction

from .models import (
    Counterparty,
    Transaction,
    Payment,
    PaymentMethod,
    CardPaymentDetail,
    ChequePaymentDetail,
    MeltedGoldDetail,
    ManufacturedGoldDetail,
    MiscGoldDetail,
    AuditLog,
    GoldCategory,
    NormalGoldType,
)


class TransactionService:

    @staticmethod
    @db_transaction.atomic
    def create_transaction(
        *,
        user,
        transaction_data,
        melted_data=None,
        manufactured_data=None,
        misc_data=None,
        payments=None,
    ):
        """
        Creates complete transaction with:
        - counterparty
        - gold details
        - payments
        - audit log
        """

        counterparty, _ = Counterparty.objects.get_or_create(
            name=transaction_data["counterparty_name"],
            defaults={
                "type": transaction_data["counterparty_type"],
                "mobile": transaction_data.get(
                    "counterparty_mobile", ""
                ),
                "national_code": transaction_data.get(
                    "counterparty_national_code", ""
                ),
                "address": transaction_data.get(
                    "counterparty_address", ""
                ),
            },
        )

        trx = Transaction.objects.create(
            branch=user.branch,
            transaction_type=transaction_data[
                "transaction_type"
            ],
            transaction_date=transaction_data[
                "transaction_date"
            ],
            counterparty=counterparty,
            created_by=user,
            gold_category=transaction_data[
                "gold_category"
            ],
            normal_gold_type=transaction_data.get(
                "normal_gold_type", ""
            ),
            gold_status=transaction_data[
                "gold_status"
            ],
            description=transaction_data.get(
                "description", ""
            ),
        )

        TransactionService._create_gold_details(
            trx=trx,
            melted_data=melted_data,
            manufactured_data=manufactured_data,
            misc_data=misc_data,
        )

        TransactionService._create_payments(
            trx=trx,
            payments=payments or [],
        )

        AuditLog.objects.create(
            user=user,
            action="create_transaction",
            model_name="Transaction",
            object_id=trx.pk,
            data={
                "transaction_type":
                    trx.transaction_type,
                "counterparty":
                    counterparty.name,
            },
        )

        return trx

    @staticmethod
    def _create_gold_details(
        *,
        trx,
        melted_data,
        manufactured_data,
        misc_data,
    ):

        if trx.gold_category == GoldCategory.MELTED:

            if not melted_data:
                return

            MeltedGoldDetail.objects.create(
                transaction=trx,
                **melted_data
            )

        elif (
            trx.gold_category == GoldCategory.NORMAL
            and trx.normal_gold_type
            == NormalGoldType.MANUFACTURED
        ):

            if not manufactured_data:
                return

            ManufacturedGoldDetail.objects.create(
                transaction=trx,
                **manufactured_data
            )

        elif (
            trx.gold_category == GoldCategory.NORMAL
            and trx.normal_gold_type
            == NormalGoldType.MISC
        ):

            if not misc_data:
                return

            MiscGoldDetail.objects.create(
                transaction=trx,
                **misc_data
            )

    @staticmethod
    def _create_payments(
        *,
        trx,
        payments,
    ):

        for item in payments:

            payment = Payment.objects.create(
                transaction=trx,
                method=item["method"],
                amount=item["amount"],
                status=item["status"],
            )

            if (
                payment.method
                == PaymentMethod.CARD
            ):

                CardPaymentDetail.objects.create(
                    payment=payment,
                    reference_number=item.get(
                        "reference_number", ""
                    ),
                    card_number=item.get(
                        "card_number", ""
                    ),
                    terminal_number=item.get(
                        "terminal_number", ""
                    ),
                )

            elif (
                payment.method
                == PaymentMethod.CHEQUE
            ):

                ChequePaymentDetail.objects.create(
                    payment=payment,
                    cheque_number=item[
                        "cheque_number"
                    ],
                    bank_name=item[
                        "bank_name"
                    ],
                    due_date=item[
                        "due_date"
                    ],
                    account_owner=item[
                        "account_owner"
                    ],
                    image=item.get(
                        "cheque_image"
                    ),
                )