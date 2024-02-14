document.addEventListener('DOMContentLoaded', function() {
    // Function to show/hide fields based on selected payment method
    function toggleFields() {
        var paymentMethod = document.getElementById('id_payment_method').value;
        // Account fields
        toggleFieldVisibility('account_name', paymentMethod === 'account');
        toggleFieldVisibility('checking_acc', paymentMethod === 'account');
        toggleFieldVisibility('routing_no', paymentMethod === 'account');
        toggleFieldVisibility('checking_no', paymentMethod === 'account');
        toggleFieldVisibility('account_address', paymentMethod === 'account');
        // Card fields
        toggleFieldVisibility('card_name', paymentMethod === 'card');
        toggleFieldVisibility('billing_address', paymentMethod === 'card');
        toggleFieldVisibility('card_no', paymentMethod === 'card');
        toggleFieldVisibility('expire_date', paymentMethod === 'card');
        toggleFieldVisibility('cvv', paymentMethod === 'card');
    }

    // Function to toggle visibility of a field
    function toggleFieldVisibility(fieldName, show) {
        var field = document.querySelector('.field-' + fieldName);
        if (field) {
            field.style.display = show ? '' : 'none';
        }
    }

    // Call the toggleFields function on page load
    toggleFields();

    // Call the toggleFields function whenever the payment method field changes
    document.getElementById('id_payment_method').addEventListener('change', function() {
        toggleFields();
    });
});
// custom_admin.js

document.addEventListener("DOMContentLoaded", function() {
    // Function to add card fields
    function addCardFields() {
        // Get the card container element
        var cardContainer = document.getElementById("card-container");

        // Get the card template
        var cardTemplate = document.getElementById("card-template").content.cloneNode(true);

        // Append the cloned card template to the card container
        cardContainer.appendChild(cardTemplate);
    }

    // Add event listener to the "Add Card" button
    var addCardButton = document.getElementById("add-card-button");
    addCardButton.addEventListener("click", addCardFields);
});
