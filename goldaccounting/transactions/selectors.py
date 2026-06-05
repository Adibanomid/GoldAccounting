# transactions/selectors.py

from django.db.models import Sum, Count, Q
from django.utils import timezone

from .models import (
    Transaction,
    Payment,
    Counterparty,
    GoldStatus,
    PaymentStatus,
)


# =====================================================
# Transactions
# =====================================================

def get_transaction_by_id(transaction_id):
    return (
        Transaction.objects
        .select_related(
            "branch",
            "counterparty",
            "created_by",
        )
        .prefetch_related(
            "payments",
        )
        .get(pk=transaction_id)
    )


def get_branch_transactions(branch):
    return (
        Transaction.objects
        .filter(branch=branch)
        .select_related(
            "counterparty",
            "created_by",
        )
        .order_by("-transaction_date")
    )


def search_transactions(
    *,
    branch=None,
    transaction_type=None,
    counterparty=None,
    from_date=None,
    to_date=None,
):
    qs = Transaction.objects.all()

    if branch:
        qs = qs.filter(branch=branch)

    if transaction_type:
        qs = qs.filter(
            transaction_type=transaction_type
        )

    if counterparty:
        qs = qs.filter(
            counterparty__name__icontains=counterparty
        )

    if from_date:
        qs = qs.filter(
            transaction_date__gte=from_date
        )

    if to_date:
        qs = qs.filter(
            transaction_date__lte=to_date
        )

    return qs.select_related(
        "counterparty",
        "branch",
    )


# =====================================================
# Counterparties
# =====================================================

def search_counterparties(query):
    return (
        Counterparty.objects
        .filter(
            Q(name__icontains=query)
            | Q(mobile__icontains=query)
        )
        .order_by("name")
    )


# =====================================================
# Pending Gold Deliveries
# =====================================================

def get_pending_gold_deliveries(branch=None):

    qs = Transaction.objects.filter(
        gold_status=GoldStatus.PENDING
    )

    if branch:
        qs = qs.filter(branch=branch)

    return qs.select_related(
        "counterparty"
    )


# =====================================================
# Pending Payments
# =====================================================

def get_pending_payments(branch=None):

    qs = Payment.objects.filter(
        status=PaymentStatus.PENDING
    )

    if branch:
        qs = qs.filter(
            transaction__branch=branch
        )

    return qs.select_related(
        "transaction",
        "transaction__counterparty",
    )


# =====================================================
# Dashboard Statistics
# =====================================================

def get_dashboard_stats(branch=None):

    transaction_qs = Transaction.objects.all()
    payment_qs = Payment.objects.all()

    if branch:
        transaction_qs = transaction_qs.filter(
            branch=branch
        )

        payment_qs = payment_qs.filter(
            transaction__branch=branch
        )

    return {
        "transactions_count":
            transaction_qs.count(),

        "pending_gold_count":
            transaction_qs.filter(
                gold_status=GoldStatus.PENDING
            ).count(),

        "pending_payment_count":
            payment_qs.filter(
                status=PaymentStatus.PENDING
            ).count(),

        "payments_total":
            payment_qs.aggregate(
                total=Sum("amount")
            )["total"] or 0,
    }


# =====================================================
# Daily Report
# =====================================================

def get_today_report(branch=None):

    today = timezone.localdate()

    qs = Transaction.objects.filter(
        transaction_date__date=today
    )

    if branch:
        qs = qs.filter(branch=branch)

    return {
        "count": qs.count(),
        "buy_count": qs.filter(
            transaction_type="buy"
        ).count(),
        "sell_count": qs.filter(
            transaction_type="sell"
        ).count(),
    }


# =====================================================
# Branch Summary
# =====================================================

def get_branch_summary(branch):

    transactions = Transaction.objects.filter(
        branch=branch
    )

    payments = Payment.objects.filter(
        transaction__branch=branch
    )

    return {
        "transactions":
            transactions.count(),

        "payments":
            payments.count(),

        "payments_total":
            payments.aggregate(
                total=Sum("amount")
            )["total"] or 0,

        "counterparties":
            Counterparty.objects.filter(
                transactions__branch=branch
            ).distinct().count(),
    }