// static/transactions/transaction.js

document.addEventListener("DOMContentLoaded", function () {
  const goldCategoryInputs = document.querySelectorAll(
    'input[name="gold_category"]'
  );

  const normalGoldTypeField = document.getElementById("normal-gold-wrapper");

  const meltedSection = document.getElementById("melted-section");

  const manufacturedSection = document.getElementById("manufactured-section");

  const miscSection = document.getElementById("misc-section");

  function getSelectedGoldCategory() {
    const selected = document.querySelector(
      'input[name="gold_category"]:checked'
    );

    return selected ? selected.value : null;
  }

  function getNormalGoldType() {
    const field = document.querySelector('select[name="normal_gold_type"]');

    return field ? field.value : null;
  }

  function updateGoldSections() {
    const category = getSelectedGoldCategory();
    const normalType = getNormalGoldType();

    meltedSection.style.display = "none";
    manufacturedSection.style.display = "none";
    miscSection.style.display = "none";

    if (normalGoldTypeField) {
      normalGoldTypeField.style.display = "none";
    }

    if (category === "melted") {
      meltedSection.style.display = "block";
    } else if (category === "normal") {
      if (normalGoldTypeField) {
        normalGoldTypeField.style.display = "block";
      }

      if (normalType === "manufactured") {
        manufacturedSection.style.display = "block";
      }

      if (normalType === "misc") {
        miscSection.style.display = "block";
      }
    }
  }

  goldCategoryInputs.forEach((input) => {
    input.addEventListener("change", updateGoldSections);
  });

  const normalTypeSelect = document.querySelector(
    'select[name="normal_gold_type"]'
  );

  if (normalTypeSelect) {
    normalTypeSelect.addEventListener("change", updateGoldSections);
  }

  updateGoldSections();

  // =====================================
  // Payment Formset
  // =====================================

  const addPaymentBtn = document.getElementById("add-payment-btn");

  const paymentsContainer = document.getElementById("payments-container");

  const totalForms = document.getElementById("id_payments-TOTAL_FORMS");

  if (addPaymentBtn && paymentsContainer && totalForms) {
    addPaymentBtn.addEventListener("click", function () {
      const paymentCards = paymentsContainer.querySelectorAll(".payment-card");

      const lastCard = paymentCards[paymentCards.length - 1];

      const newIndex = parseInt(totalForms.value);

      const clone = lastCard.cloneNode(true);

      clone.querySelectorAll("input, select, textarea").forEach((field) => {
        if (field.name) {
          field.name = field.name.replace(
            /payments-\d+/g,
            `payments-${newIndex}`
          );
        }

        if (field.id) {
          field.id = field.id.replace(/payments-\d+/g, `payments-${newIndex}`);
        }

        if (field.type !== "hidden" && field.type !== "checkbox") {
          field.value = "";
        }
      });

      clone.querySelectorAll("label").forEach((label) => {
        if (label.htmlFor) {
          label.htmlFor = label.htmlFor.replace(
            /payments-\d+/g,
            `payments-${newIndex}`
          );
        }
      });

      paymentsContainer.appendChild(clone);

      totalForms.value = newIndex + 1;
    });
  }

  // =====================================
  // Payment Method Toggle
  // =====================================

  function updatePaymentFields(card) {
    const methodSelect = card.querySelector('select[name$="-method"]');

    if (!methodSelect) return;

    const method = methodSelect.value;

    const referenceNumber = card
      .querySelector('input[name$="-reference_number"]')
      ?.closest("div");

    const cardNumber = card
      .querySelector('input[name$="-card_number"]')
      ?.closest("div");

    const terminalNumber = card
      .querySelector('input[name$="-terminal_number"]')
      ?.closest("div");

    const chequeNumber = card
      .querySelector('input[name$="-cheque_number"]')
      ?.closest("div");

    const bankName = card
      .querySelector('input[name$="-bank_name"]')
      ?.closest("div");

    const dueDate = card
      .querySelector('input[name$="-due_date"]')
      ?.closest("div");

    const accountOwner = card
      .querySelector('input[name$="-account_owner"]')
      ?.closest("div");

    const chequeImage = card.querySelector(
      'input[name$="-cheque_image"]'
    )?.parentElement;

    [
      referenceNumber,
      cardNumber,
      terminalNumber,
      chequeNumber,
      bankName,
      dueDate,
      accountOwner,
      chequeImage,
    ].forEach((el) => {
      if (el) el.style.display = "none";
    });

    if (method === "card") {
      [referenceNumber, cardNumber, terminalNumber].forEach((el) => {
        if (el) el.style.display = "block";
      });
    } else if (method === "cheque") {
      [chequeNumber, bankName, dueDate, accountOwner, chequeImage].forEach(
        (el) => {
          if (el) el.style.display = "block";
        }
      );
    }
  }

  function initializePayments() {
    document.querySelectorAll(".payment-card").forEach((card) => {
      const methodSelect = card.querySelector('select[name$="-method"]');

      if (!methodSelect) return;

      methodSelect.addEventListener("change", () => updatePaymentFields(card));

      updatePaymentFields(card);
    });
  }

  initializePayments();
});
