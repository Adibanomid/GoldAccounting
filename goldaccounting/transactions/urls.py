# transactions/urls.py

from django.urls import path

from .views import (
    TransactionCreateView,
    TransactionDetailView,
)

app_name = "transactions"

urlpatterns = [

    # -----------------------------------------
    # Create Transaction
    # -----------------------------------------

    path(
        "create/",
        TransactionCreateView.as_view(),
        name="create",
    ),

    # -----------------------------------------
    # Transaction Detail
    # -----------------------------------------

    path(
        "<int:pk>/",
        TransactionDetailView.as_view(),
        name="detail",
    ),
]