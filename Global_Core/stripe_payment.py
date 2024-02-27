import stripe


# Set your secret API key
stripe.api_key = "sk_test_51OlnMEI2KysFcOYIr0VF0wDzn7MXL3b8gqAMwWgTFTknOfrBif7IlTNybkNVL6MRVnZyfggGyf8DCQejI58HY4TF004pAsr1D1"


def authorize_stripe(amount):
    print("Amount:", amount)
    try:
        authorization = stripe.Charge.create(
            amount= amount,
            currency="usd",
            source="tok_visa",
            description="Example authorization",
            capture=False
        )
        charge_id = authorization.id
        capture = stripe.Charge.capture(
                charge_id,  # Charge ID obtained from the authorization
                amount=amount  # Amount to capture in cents
        )
        print("Authorization successful")
        # Get the charge ID for later capture
        charge_id = authorization.id
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        print("Card declined")
    except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
        print("Rate limit exceeded")
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        print("Invalid parameters")
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        print("Authentication failed")
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        print("Network error")
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        print("Something went wrong. Please try again.")
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        print("Something went wrong. Please try again.")


# Later, when you want to capture the authorized payment
# try:
#     charge_id = authorization.id
#     capture = stripe.Charge.capture(
#         charge_id,  # Charge ID obtained from the authorization
#         amount=1000  # Amount to capture in cents
#     )
#     print("Capture successful")
# except stripe.error.StripeError as e:
#     # Display a very generic error to the user, and maybe send
#     # yourself an email
#     print("Capture failed. Please try again.")