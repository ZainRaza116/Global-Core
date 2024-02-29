
    document.addEventListener("DOMContentLoaded", function() {
        var paymentMethodField = document.getElementById("id_payment_method");
        var cardContainer = document.getElementById("card-container");

        // Function to toggle visibility of card fields
        function toggleCardFields() {
            if (paymentMethodField.value === 'card') {
                cardContainer.style.display = "block";
            } else {
                cardContainer.style.display = "none";
            }
        }

        // Initial toggle on page load
        toggleCardFields();

        // Bind change event to payment method field
        paymentMethodField.addEventListener("change", toggleCardFields);
    });

